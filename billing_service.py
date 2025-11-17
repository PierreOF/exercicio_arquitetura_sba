"""
Billing Microservice
Porta: 8003
Responsabilidades: Processamento de pagamentos e cobranças
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from datetime import datetime
import uvicorn
import logging
import random

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[BILLING-SERVICE] %(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Billing Service", version="1.0.0", docs_url=None, redoc_url=None)

# Armazenamento em memória
TRANSACTIONS_DB: Dict[int, dict] = {}
NEXT_TRANSACTION_ID = 5000

# Modelos Pydantic
class ChargeRequest(BaseModel):
    order_id: int
    amount: float
    payment_method: str = "credit_card"

class TransactionResponse(BaseModel):
    transaction_id: int
    order_id: int
    amount: float
    status: str
    payment_method: str
    processed_at: str
    message: str

# Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "billing"}

@app.post("/billing/charge", response_model=TransactionResponse, status_code=201)
async def charge_payment(charge: ChargeRequest):
    """Processar pagamento"""
    global NEXT_TRANSACTION_ID

    logger.info(f"Processando pagamento: order_id={charge.order_id}, amount={charge.amount}")

    # Validar amount
    if charge.amount <= 0:
        logger.warning(f"Amount inválido: {charge.amount}")
        raise HTTPException(status_code=400, detail="Amount deve ser maior que zero")

    # Simular processamento de pagamento (90% de sucesso)
    success = random.random() < 0.9

    transaction_id = NEXT_TRANSACTION_ID
    NEXT_TRANSACTION_ID += 1

    if success:
        status = "paid"
        message = "Pagamento processado com sucesso"
        logger.info(f"Pagamento aprovado: transaction_id={transaction_id}")
    else:
        status = "failed"
        message = "Falha no processamento do pagamento"
        logger.warning(f"Pagamento recusado: transaction_id={transaction_id}")

    transaction_data = {
        "transaction_id": transaction_id,
        "order_id": charge.order_id,
        "amount": charge.amount,
        "status": status,
        "payment_method": charge.payment_method,
        "processed_at": datetime.now().isoformat(),
        "message": message
    }

    TRANSACTIONS_DB[transaction_id] = transaction_data

    return transaction_data

@app.get("/billing/transaction/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int):
    """Buscar transação por ID"""
    logger.info(f"Buscando transação: transaction_id={transaction_id}")

    transaction_data = TRANSACTIONS_DB.get(transaction_id)

    if not transaction_data:
        logger.warning(f"Transação não encontrada: transaction_id={transaction_id}")
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    logger.info(f"Transação encontrada: transaction_id={transaction_id}")
    return transaction_data

@app.get("/billing/order/{order_id}")
async def get_order_transactions(order_id: int):
    """Listar todas as transações de um pedido"""
    logger.info(f"Buscando transações do pedido: order_id={order_id}")

    order_transactions = [
        tx for tx in TRANSACTIONS_DB.values()
        if tx["order_id"] == order_id
    ]

    logger.info(f"Encontradas {len(order_transactions)} transações para order_id={order_id}")
    return {"transactions": order_transactions, "total": len(order_transactions)}

@app.get("/billing/transactions")
async def list_all_transactions():
    """Listar todas as transações"""
    logger.info(f"Listando {len(TRANSACTIONS_DB)} transações")
    return {"transactions": list(TRANSACTIONS_DB.values()), "total": len(TRANSACTIONS_DB)}

@app.post("/billing/refund/{transaction_id}")
async def refund_transaction(transaction_id: int):
    """Processar reembolso de uma transação"""
    logger.info(f"Processando reembolso: transaction_id={transaction_id}")

    transaction_data = TRANSACTIONS_DB.get(transaction_id)

    if not transaction_data:
        logger.warning(f"Transação não encontrada: transaction_id={transaction_id}")
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    if transaction_data["status"] != "paid":
        logger.warning(f"Transação não pode ser reembolsada: status={transaction_data['status']}")
        raise HTTPException(status_code=400, detail="Apenas transações pagas podem ser reembolsadas")

    transaction_data["status"] = "refunded"
    transaction_data["message"] = "Reembolso processado com sucesso"

    logger.info(f"Reembolso concluído: transaction_id={transaction_id}")
    return transaction_data

if __name__ == "__main__":
    logger.info("Iniciando Billing Service na porta 8003")
    uvicorn.run(app, host="0.0.0.0", port=8003)
