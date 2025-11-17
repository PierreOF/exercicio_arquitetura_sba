"""
Cliente de Teste para Simulação de Microserviços
Demonstra o fluxo completo através do Gateway
"""
import httpx
import asyncio
import sys
from typing import Dict, Any

# Cores para output
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

GATEWAY_URL = "http://localhost:8000"

def print_section(title: str):
    """Imprimir título de seção"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title:^60}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.NC}\n")

def print_success(message: str):
    """Imprimir mensagem de sucesso"""
    print(f"{Colors.GREEN}✓ {message}{Colors.NC}")

def print_error(message: str):
    """Imprimir mensagem de erro"""
    print(f"{Colors.RED}✗ {message}{Colors.NC}")

def print_info(label: str, value: Any):
    """Imprimir informação"""
    print(f"{Colors.CYAN}{label}:{Colors.NC} {value}")

async def check_health():
    """Verificar saúde de todos os serviços"""
    print_section("VERIFICANDO SAÚDE DOS SERVIÇOS")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{GATEWAY_URL}/health")
            data = response.json()

            print_info("Gateway Status", data["status"])
            print()

            for service, status in data["services"].items():
                if status == "healthy":
                    print_success(f"{service.capitalize()} Service: {status}")
                else:
                    print_error(f"{service.capitalize()} Service: {status}")

            if data["status"] != "healthy":
                print_error("\nAlguns serviços não estão saudáveis. Verifique os logs.")
                return False

            print_success("\nTodos os serviços estão operacionais!")
            return True

    except Exception as e:
        print_error(f"Erro ao verificar saúde dos serviços: {str(e)}")
        print_error("Certifique-se de que todos os serviços estão rodando (execute ./run_all.sh)")
        return False

async def register_user(name: str, email: str) -> Dict[str, Any]:
    """Registrar novo usuário"""
    print_section("REGISTRANDO USUÁRIO")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GATEWAY_URL}/gateway/register",
                json={"name": name, "email": email}
            )
            response.raise_for_status()
            data = response.json()

            print_success(f"Usuário registrado com sucesso!")
            print_info("User ID", data["user"]["user_id"])
            print_info("Nome", data["user"]["name"])
            print_info("Email", data["user"]["email"])

            return data["user"]

    except httpx.HTTPStatusError as e:
        print_error(f"Erro HTTP: {e.response.status_code}")
        print_error(f"Detalhes: {e.response.json().get('detail', 'Erro desconhecido')}")
        return None
    except Exception as e:
        print_error(f"Erro ao registrar usuário: {str(e)}")
        return None

async def login_user(email: str) -> Dict[str, Any]:
    """Fazer login de usuário"""
    print_section("FAZENDO LOGIN")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GATEWAY_URL}/gateway/login",
                json={"email": email}
            )
            response.raise_for_status()
            data = response.json()

            print_success(f"Login realizado com sucesso!")
            print_info("User ID", data["user"]["user_id"])
            print_info("Nome", data["user"]["name"])

            return data["user"]

    except httpx.HTTPStatusError as e:
        print_error(f"Erro HTTP: {e.response.status_code}")
        print_error(f"Detalhes: {e.response.json().get('detail', 'Erro desconhecido')}")
        return None
    except Exception as e:
        print_error(f"Erro ao fazer login: {str(e)}")
        return None

async def make_purchase(user_id: int, amount: float, product_name: str) -> Dict[str, Any]:
    """Realizar compra"""
    print_section("PROCESSANDO COMPRA")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{GATEWAY_URL}/gateway/purchase",
                json={
                    "user_id": user_id,
                    "amount": amount,
                    "product_name": product_name,
                    "payment_method": "credit_card"
                }
            )
            response.raise_for_status()
            data = response.json()

            # Informações do usuário
            print(f"{Colors.YELLOW}Usuário:{Colors.NC}")
            print_info("  Nome", data["user"]["name"])
            print_info("  Email", data["user"]["email"])
            print()

            # Informações do pedido
            print(f"{Colors.YELLOW}Pedido:{Colors.NC}")
            print_info("  Order ID", data["order"]["order_id"])
            print_info("  Produto", data["order"]["product_name"])
            print_info("  Valor", f"R$ {data['order']['amount']:.2f}")
            print_info("  Status", data["order"]["status"])
            print()

            # Informações da transação
            print(f"{Colors.YELLOW}Pagamento:{Colors.NC}")
            print_info("  Transaction ID", data["transaction"]["transaction_id"])
            print_info("  Status", data["transaction"]["status"])
            print_info("  Método", data["transaction"]["payment_method"])
            print_info("  Mensagem", data["transaction"]["message"])
            print()

            if data["purchase_status"] == "paid":
                print_success(f"Compra realizada com sucesso!")
            else:
                print_error(f"Falha no pagamento!")

            return data

    except httpx.HTTPStatusError as e:
        print_error(f"Erro HTTP: {e.response.status_code}")
        print_error(f"Detalhes: {e.response.json().get('detail', 'Erro desconhecido')}")
        return None
    except Exception as e:
        print_error(f"Erro ao processar compra: {str(e)}")
        return None

async def get_user_orders(user_id: int):
    """Buscar pedidos do usuário"""
    print_section("CONSULTANDO PEDIDOS DO USUÁRIO")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{GATEWAY_URL}/gateway/user/{user_id}/orders")
            response.raise_for_status()
            data = response.json()

            print_info("Total de pedidos", data["total_orders"])
            print()

            if data["total_orders"] > 0:
                for i, order in enumerate(data["orders"], 1):
                    print(f"{Colors.CYAN}Pedido {i}:{Colors.NC}")
                    print_info("  Order ID", order["order_id"])
                    print_info("  Produto", order["product_name"])
                    print_info("  Valor", f"R$ {order['amount']:.2f}")
                    print_info("  Status", order["status"])
                    print_info("  Data", order["created_at"])
                    print()
            else:
                print_info("Status", "Nenhum pedido encontrado")

    except Exception as e:
        print_error(f"Erro ao buscar pedidos: {str(e)}")

async def run_demo():
    """Executar demonstração completa"""
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                            ║")
    print("║   DEMONSTRAÇÃO DE ARQUITETURA DE MICROSERVIÇOS             ║")
    print("║   Gateway + Users + Orders + Billing                       ║")
    print("║                                                            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.NC}")

    # 1. Verificar saúde dos serviços
    if not await check_health():
        sys.exit(1)

    await asyncio.sleep(1)

    # 2. Registrar usuário
    user = await register_user("João Silva", "joao.silva@email.com")
    if not user:
        sys.exit(1)

    await asyncio.sleep(1)

    # 3. Fazer login
    user = await login_user("joao.silva@email.com")
    if not user:
        sys.exit(1)

    await asyncio.sleep(1)

    # 4. Realizar primeira compra
    purchase1 = await make_purchase(user["user_id"], 150.00, "Notebook Dell")
    await asyncio.sleep(1)

    # 5. Realizar segunda compra
    purchase2 = await make_purchase(user["user_id"], 45.50, "Mouse Logitech")
    await asyncio.sleep(1)

    # 6. Realizar terceira compra
    purchase3 = await make_purchase(user["user_id"], 89.90, "Teclado Mecânico")
    await asyncio.sleep(1)

    # 7. Consultar pedidos do usuário
    await get_user_orders(user["user_id"])

    # Resumo final
    print_section("DEMONSTRAÇÃO CONCLUÍDA")
    print_success("Fluxo completo executado com sucesso!")
    print()
    print(f"{Colors.CYAN}Fluxo de comunicação demonstrado:{Colors.NC}")
    print("  1. Cliente → Gateway → Users Service (registro)")
    print("  2. Cliente → Gateway → Users Service (login)")
    print("  3. Cliente → Gateway → Users Service (validação)")
    print("  4. Gateway → Orders Service (criação de pedido)")
    print("  5. Gateway → Billing Service (processamento de pagamento)")
    print("  6. Gateway → Orders Service (atualização de status)")
    print()

if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Demonstração interrompida pelo usuário{Colors.NC}")
    except Exception as e:
        print_error(f"Erro na demonstração: {str(e)}")
        sys.exit(1)
