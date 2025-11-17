#!/bin/bash

echo "=========================================="
echo "Iniciando Arquitetura de Microserviços"
echo "=========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para matar processos ao sair
cleanup() {
    echo ""
    echo -e "${RED}Encerrando todos os serviços...${NC}"
    kill $(jobs -p) 2>/dev/null
    wait
    echo -e "${GREEN}Todos os serviços foram encerrados.${NC}"
    exit 0
}

# Configurar trap para Ctrl+C
trap cleanup SIGINT SIGTERM

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Erro: Python3 não está instalado${NC}"
    exit 1
fi

# Verificar se as dependências estão instaladas
echo -e "${YELLOW}Verificando dependências...${NC}"
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Instalando dependências...${NC}"
    pip3 install -r requirements.txt
fi

echo ""
echo -e "${GREEN}Iniciando serviços...${NC}"
echo ""

# Iniciar Users Service
echo -e "${GREEN}[1/4] Iniciando Users Service (porta 8001)...${NC}"
python3 users_service.py > logs_users.log 2>&1 &
USERS_PID=$!
sleep 2

# Iniciar Orders Service
echo -e "${PURPLE}[2/4] Iniciando Orders Service (porta 8002)...${NC}"
python3 orders_service.py > logs_orders.log 2>&1 &
ORDERS_PID=$!
sleep 2

# Iniciar Billing Service
echo -e "${CYAN}[3/4] Iniciando Billing Service (porta 8003)...${NC}"
python3 billing_service.py > logs_billing.log 2>&1 &
BILLING_PID=$!
sleep 2

# Iniciar Gateway
echo -e "${YELLOW}[4/4] Iniciando API Gateway (porta 8000)...${NC}"
python3 gateway.py > logs_gateway.log 2>&1 &
GATEWAY_PID=$!
sleep 3

echo ""
echo -e "${GREEN}=========================================="
echo "Todos os serviços estão rodando!"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}URLs dos serviços:${NC}"
echo -e "  ${YELLOW}Gateway:${NC}  http://localhost:8000"
echo -e "  ${GREEN}Users:${NC}    http://localhost:8001"
echo -e "  ${PURPLE}Orders:${NC}   http://localhost:8002"
echo -e "  ${CYAN}Billing:${NC}  http://localhost:8003"
echo ""
echo -e "${BLUE}Documentação interativa (Swagger):${NC}"
echo -e "  Gateway:  http://localhost:8000/docs"
echo -e "  Users:    http://localhost:8001/docs"
echo -e "  Orders:   http://localhost:8002/docs"
echo -e "  Billing:  http://localhost:8003/docs"
echo ""
echo -e "${BLUE}Logs dos serviços:${NC}"
echo -e "  tail -f logs_gateway.log"
echo -e "  tail -f logs_users.log"
echo -e "  tail -f logs_orders.log"
echo -e "  tail -f logs_billing.log"
echo ""
echo -e "${YELLOW}Pressione Ctrl+C para parar todos os serviços${NC}"
echo ""

# Aguardar indefinidamente
wait
