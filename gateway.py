"""
API Gateway
Porta: 8000
Responsabilidades: Orquestração de requisições entre microserviços
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import httpx
import uvicorn
import logging
from typing import Optional
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[GATEWAY] %(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar app FastAPI sem Swagger
app = FastAPI(
    title="API Gateway",
    version="1.0.0",
    docs_url=None,  # Desabilitar Swagger UI
    redoc_url=None  # Desabilitar ReDoc
)

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URLs dos microserviços
USERS_SERVICE_URL = "http://localhost:8001"
ORDERS_SERVICE_URL = "http://localhost:8002"
BILLING_SERVICE_URL = "http://localhost:8003"

# Timeout para requisições (em segundos)
REQUEST_TIMEOUT = 5.0

# Modelos Pydantic
class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr

class LoginRequest(BaseModel):
    email: EmailStr

class PurchaseRequest(BaseModel):
    user_id: int
    amount: float
    product_name: str = "Produto Genérico"
    payment_method: str = "credit_card"

# Funções auxiliares
async def call_service(method: str, url: str, json_data: Optional[dict] = None):
    """Realizar chamada HTTP para um microserviço"""
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=json_data)
            elif method == "PUT":
                response = await client.put(url, json=json_data)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")

            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException:
        logger.error(f"Timeout ao chamar {url}")
        raise HTTPException(status_code=504, detail="Serviço não respondeu a tempo")
    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP ao chamar {url}: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail", "Erro no serviço"))
    except Exception as e:
        logger.error(f"Erro ao chamar {url}: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Serviço indisponível: {str(e)}")

# Endpoints do Gateway
@app.get("/health")
async def health_check():
    """Health check do gateway e todos os serviços"""
    services_status = {}

    # Verificar cada serviço
    services = {
        "users": f"{USERS_SERVICE_URL}/health",
        "orders": f"{ORDERS_SERVICE_URL}/health",
        "billing": f"{BILLING_SERVICE_URL}/health"
    }

    for service_name, health_url in services.items():
        try:
            result = await call_service("GET", health_url)
            services_status[service_name] = result.get("status", "unknown")
        except Exception:
            services_status[service_name] = "unhealthy"

    all_healthy = all(status == "healthy" for status in services_status.values())

    return {
        "status": "healthy" if all_healthy else "degraded",
        "service": "gateway",
        "services": services_status
    }

@app.post("/gateway/register")
async def register_user(user: UserCreateRequest):
    """Criar novo usuário via gateway"""
    logger.info(f"[GATEWAY] Registrando usuário: {user.email}")

    user_data = await call_service(
        "POST",
        f"{USERS_SERVICE_URL}/users/create",
        {"name": user.name, "email": user.email}
    )

    logger.info(f"[GATEWAY] Usuário registrado: user_id={user_data['user_id']}")
    return {
        "message": "Usuário criado com sucesso",
        "user": user_data
    }

@app.post("/gateway/login")
async def login_user(credentials: LoginRequest):
    """Autenticar usuário via gateway"""
    logger.info(f"[GATEWAY] Autenticando usuário: {credentials.email}")

    user_data = await call_service(
        "POST",
        f"{USERS_SERVICE_URL}/users/login",
        {"email": credentials.email}
    )

    logger.info(f"[GATEWAY] Login bem-sucedido: user_id={user_data['user_id']}")
    return {
        "message": "Login realizado com sucesso",
        "user": user_data
    }

@app.post("/gateway/purchase")
async def process_purchase(purchase: PurchaseRequest):
    """
    Processar compra completa - orquestra chamadas para Users, Orders e Billing
    Fluxo: Gateway -> Users (validar) -> Orders (criar) -> Billing (cobrar)
    """
    logger.info(f"[GATEWAY] Iniciando processamento de compra para user_id={purchase.user_id}")

    try:
        # 1. Validar usuário
        logger.info(f"[GATEWAY] Passo 1/3: Validando usuário {purchase.user_id}")
        user_data = await call_service(
            "GET",
            f"{USERS_SERVICE_URL}/users/{purchase.user_id}"
        )
        logger.info(f"[GATEWAY] Usuário validado: {user_data['email']}")

        # 2. Criar pedido
        logger.info(f"[GATEWAY] Passo 2/3: Criando pedido")
        order_data = await call_service(
            "POST",
            f"{ORDERS_SERVICE_URL}/orders/create",
            {
                "user_id": purchase.user_id,
                "amount": purchase.amount,
                "product_name": purchase.product_name
            }
        )
        logger.info(f"[GATEWAY] Pedido criado: order_id={order_data['order_id']}")

        # 3. Processar pagamento
        logger.info(f"[GATEWAY] Passo 3/3: Processando pagamento")
        billing_data = await call_service(
            "POST",
            f"{BILLING_SERVICE_URL}/billing/charge",
            {
                "order_id": order_data["order_id"],
                "amount": purchase.amount,
                "payment_method": purchase.payment_method
            }
        )
        logger.info(f"[GATEWAY] Pagamento processado: status={billing_data['status']}")

        # 4. Atualizar status do pedido baseado no pagamento
        order_status = "completed" if billing_data["status"] == "paid" else "payment_failed"
        await call_service(
            "PUT",
            f"{ORDERS_SERVICE_URL}/orders/{order_data['order_id']}/status?status={order_status}"
        )
        logger.info(f"[GATEWAY] Status do pedido atualizado: {order_status}")

        # Resultado final
        result = {
            "message": "Compra processada com sucesso" if billing_data["status"] == "paid" else "Falha no pagamento",
            "purchase_status": billing_data["status"],
            "user": user_data,
            "order": order_data,
            "transaction": billing_data
        }

        logger.info(f"[GATEWAY] Compra finalizada: order_id={order_data['order_id']}, status={billing_data['status']}")
        return result

    except HTTPException as e:
        logger.error(f"[GATEWAY] Erro no processamento da compra: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"[GATEWAY] Erro inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar compra: {str(e)}")

@app.get("/gateway/user/{user_id}/orders")
async def get_user_orders(user_id: int):
    """Buscar todos os pedidos de um usuário"""
    logger.info(f"[GATEWAY] Buscando pedidos do usuário {user_id}")

    # Validar usuário
    user_data = await call_service("GET", f"{USERS_SERVICE_URL}/users/{user_id}")

    # Buscar pedidos
    orders_data = await call_service("GET", f"{ORDERS_SERVICE_URL}/orders/user/{user_id}")

    return {
        "user": user_data,
        "orders": orders_data["orders"],
        "total_orders": orders_data["total"]
    }

@app.get("/")
async def root():
    """Servir a interface web"""
    return FileResponse("frontend/index.html")

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="frontend"), name="static")

if __name__ == "__main__":
    logger.info("Iniciando API Gateway na porta 8000")
    logger.info("Interface web disponível em: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
