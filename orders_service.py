"""
Orders Microservice
Porta: 8002
Responsabilidades: Gerenciamento de pedidos (criar, buscar, listar)
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime
import uvicorn
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[ORDERS-SERVICE] %(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Orders Service", version="1.0.0", docs_url=None, redoc_url=None)

# Armazenamento em memória
ORDERS_DB: Dict[int, dict] = {}
NEXT_ORDER_ID = 1000

# Modelos Pydantic
class OrderCreate(BaseModel):
    user_id: int
    amount: float
    product_name: str = "Produto Genérico"

class OrderResponse(BaseModel):
    order_id: int
    user_id: int
    amount: float
    product_name: str
    status: str
    created_at: str

# Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "orders"}

@app.post("/orders/create", response_model=OrderResponse, status_code=201)
async def create_order(order: OrderCreate):
    """Criar novo pedido"""
    global NEXT_ORDER_ID

    logger.info(f"Criando pedido para user_id={order.user_id}, amount={order.amount}")

    # Validar amount
    if order.amount <= 0:
        logger.warning(f"Amount inválido: {order.amount}")
        raise HTTPException(status_code=400, detail="Amount deve ser maior que zero")

    # Criar pedido
    order_id = NEXT_ORDER_ID
    NEXT_ORDER_ID += 1

    order_data = {
        "order_id": order_id,
        "user_id": order.user_id,
        "amount": order.amount,
        "product_name": order.product_name,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }

    ORDERS_DB[order_id] = order_data

    logger.info(f"Pedido criado com sucesso: order_id={order_id}")
    return order_data

@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int):
    """Buscar pedido por ID"""
    logger.info(f"Buscando pedido: order_id={order_id}")

    order_data = ORDERS_DB.get(order_id)

    if not order_data:
        logger.warning(f"Pedido não encontrado: order_id={order_id}")
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    logger.info(f"Pedido encontrado: order_id={order_id}")
    return order_data

@app.put("/orders/{order_id}/status")
async def update_order_status(order_id: int, status: str):
    """Atualizar status do pedido"""
    logger.info(f"Atualizando status do pedido {order_id} para {status}")

    order_data = ORDERS_DB.get(order_id)

    if not order_data:
        logger.warning(f"Pedido não encontrado: order_id={order_id}")
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    order_data["status"] = status
    logger.info(f"Status atualizado: order_id={order_id}, status={status}")

    return order_data

@app.get("/orders/user/{user_id}")
async def get_user_orders(user_id: int):
    """Listar todos os pedidos de um usuário"""
    logger.info(f"Buscando pedidos do usuário: user_id={user_id}")

    user_orders = [order for order in ORDERS_DB.values() if order["user_id"] == user_id]

    logger.info(f"Encontrados {len(user_orders)} pedidos para user_id={user_id}")
    return {"orders": user_orders, "total": len(user_orders)}

@app.get("/orders")
async def list_all_orders():
    """Listar todos os pedidos"""
    logger.info(f"Listando {len(ORDERS_DB)} pedidos")
    return {"orders": list(ORDERS_DB.values()), "total": len(ORDERS_DB)}

if __name__ == "__main__":
    logger.info("Iniciando Orders Service na porta 8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
