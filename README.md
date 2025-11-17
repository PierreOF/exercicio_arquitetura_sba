# Simulação de Arquitetura de Microserviços

Uma implementação completa de arquitetura de microserviços usando Python e FastAPI, demonstrando comunicação entre serviços através de um API Gateway.

## 📋 Arquitetura

```
┌─────────────────────┐
│    Interface Web    │  (http://localhost:8000)
│  (frontend/...)     │  • Registro/Login
└──────────┬──────────┘  • Realizar Compras
           │             • Visualizar Pedidos
           ▼
┌─────────────────────┐
│      Gateway        │  Porta 8000
│    (gateway.py)     │  • Orquestração de requisições
└──────┬──┬───┬───────┘  • Roteamento entre serviços
       │  │   │          • Composição de respostas
       │  │   │
   ┌───┘  │   └────┐
   │      │        │
   ▼      ▼        ▼
┌─────┐ ┌─────┐ ┌─────┐
│Users│ │Orders│ │Billing│
│8001 │ │8002 │ │8003 │
└─────┘ └─────┘ └─────┘
```

## 🚀 Serviços

### 1. **Users Service** (Porta 8001)
Gerenciamento de usuários
- `POST /users/create` - Criar usuário
- `POST /users/login` - Autenticar usuário
- `GET /users/{user_id}` - Buscar usuário
- `GET /users` - Listar todos os usuários

### 2. **Orders Service** (Porta 8002)
Gerenciamento de pedidos
- `POST /orders/create` - Criar pedido
- `GET /orders/{order_id}` - Buscar pedido
- `PUT /orders/{order_id}/status` - Atualizar status
- `GET /orders/user/{user_id}` - Pedidos de um usuário
- `GET /orders` - Listar todos os pedidos

### 3. **Billing Service** (Porta 8003)
Processamento de pagamentos
- `POST /billing/charge` - Processar pagamento
- `GET /billing/transaction/{transaction_id}` - Buscar transação
- `GET /billing/order/{order_id}` - Transações de um pedido
- `POST /billing/refund/{transaction_id}` - Processar reembolso
- `GET /billing/transactions` - Listar todas as transações

### 4. **API Gateway** (Porta 8000)
Orquestração e roteamento
- `GET /health` - Status de todos os serviços
- `POST /gateway/register` - Registrar usuário
- `POST /gateway/login` - Autenticar usuário
- `POST /gateway/purchase` - Processar compra completa
- `GET /gateway/user/{user_id}/orders` - Pedidos do usuário

## 📦 Requisitos

- Python 3.8+
- Dependências (veja `requirements.txt`):
  - fastapi
  - uvicorn
  - httpx
  - pydantic

## 🔧 Instalação

1. **Clone ou navegue até o diretório do projeto:**
```bash
cd /home/pierremonteiro/Desktop/ES/E.S/6P/Arquitetura/SBA
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

## ▶️ Executando os Serviços

### Opção 1: Iniciar todos os serviços de uma vez (Recomendado)

```bash
./run_all.sh
```

Este script irá:
- Verificar dependências
- Iniciar todos os 4 serviços em ordem
- Criar logs separados para cada serviço
- Exibir URLs e documentação
- Aguardar até você pressionar `Ctrl+C`

### Opção 2: Iniciar serviços individualmente

Em terminais separados:

```bash
# Terminal 1 - Users Service
python3 users_service.py

# Terminal 2 - Orders Service
python3 orders_service.py

# Terminal 3 - Billing Service
python3 billing_service.py

# Terminal 4 - Gateway
python3 gateway.py
```

## 🌐 Acessando a Interface Web

Após iniciar os serviços, acesse:

**http://localhost:8000**

A interface web permite:
- ✅ Criar conta de usuário
- ✅ Fazer login
- ✅ Realizar compras
- ✅ Visualizar histórico de pedidos
- ✅ Monitorar saúde dos serviços em tempo real
- ✅ Ver arquitetura do sistema

A interface é **responsiva** e funciona em desktop, tablet e mobile.

## 🧪 Testando a Aplicação

### 1. Interface Web (Recomendado):

Abra http://localhost:8000 no navegador e use a interface gráfica.

### 2. Executar demonstração automática (CLI):

```bash
python3 test_client.py
```

Este script demonstra o fluxo completo via terminal:
1. Verificação de saúde dos serviços
2. Registro de usuário
3. Login
4. Múltiplas compras (validação → pedido → pagamento)
5. Consulta de pedidos

### 3. Testar manualmente com curl:

**Verificar saúde dos serviços:**
```bash
curl http://localhost:8000/health
```

**Registrar usuário:**
```bash
curl -X POST http://localhost:8000/gateway/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Maria Silva", "email": "maria@email.com"}'
```

**Fazer login:**
```bash
curl -X POST http://localhost:8000/gateway/login \
  -H "Content-Type: application/json" \
  -d '{"email": "maria@email.com"}'
```

**Realizar compra:**
```bash
curl -X POST http://localhost:8000/gateway/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "amount": 99.90,
    "product_name": "Notebook",
    "payment_method": "credit_card"
  }'
```

**Consultar pedidos do usuário:**
```bash
curl http://localhost:8000/gateway/user/1/orders
```


## 📊 Fluxo de Compra

Quando uma compra é processada através do endpoint `/gateway/purchase`, o seguinte fluxo ocorre:

```
1. Cliente → Gateway
   POST /gateway/purchase
   {
     "user_id": 1,
     "amount": 150.00,
     "product_name": "Produto X"
   }

2. Gateway → Users Service
   GET /users/1
   (Valida se o usuário existe)

3. Gateway → Orders Service
   POST /orders/create
   (Cria o pedido com status "pending")

4. Gateway → Billing Service
   POST /billing/charge
   (Processa o pagamento - 90% de taxa de sucesso simulada)

5. Gateway → Orders Service
   PUT /orders/{order_id}/status
   (Atualiza status para "completed" ou "payment_failed")

6. Gateway → Cliente
   Retorna resultado agregado com:
   - Dados do usuário
   - Dados do pedido
   - Dados da transação
```

## 📝 Logs

Os logs de cada serviço são salvos em arquivos separados:
- `logs_gateway.log` - Logs do Gateway
- `logs_users.log` - Logs do Users Service
- `logs_orders.log` - Logs do Orders Service
- `logs_billing.log` - Logs do Billing Service

Para visualizar logs em tempo real:
```bash
tail -f logs_gateway.log
tail -f logs_users.log
tail -f logs_orders.log
tail -f logs_billing.log
```

## 🔍 Características da Implementação

### ✅ Implementado

- **Interface Web Moderna**: Interface gráfica responsiva em HTML/CSS/JavaScript
- **Separação de serviços**: Cada microserviço roda em porta independente
- **API Gateway**: Orquestração centralizada de requisições
- **Comunicação assíncrona**: Uso de `httpx` e `async/await`
- **CORS configurado**: Permite chamadas da interface web
- **Validação de dados**: Modelos Pydantic com validação de tipos
- **Logging estruturado**: Cada serviço tem logging próprio
- **Health checks**: Endpoint de saúde em cada serviço com monitoramento em tempo real
- **Tratamento de erros**: Erros HTTP apropriados e timeout
- **Armazenamento em memória**: Simulação de banco de dados
- **Persistência de sessão**: LocalStorage para manter usuário logado

### 🎯 Conceitos Demonstrados

1. **Microserviços**: Serviços independentes com responsabilidades bem definidas
2. **API Gateway Pattern**: Ponto de entrada único para clientes
3. **Service Discovery**: Gateway conhece as URLs de todos os serviços
4. **Orquestração**: Gateway coordena múltiplas chamadas de serviço
5. **Comunicação inter-serviços**: HTTP/REST entre microserviços
6. **Separação de responsabilidades**: Cada serviço tem seu domínio

## 🛠️ Melhorias Futuras

Para uma implementação de produção, considere adicionar:

- [ ] Banco de dados real (PostgreSQL, MongoDB)
- [ ] Autenticação e autorização (JWT, OAuth2)
- [ ] Service Discovery dinâmico (Consul, Eureka)
- [ ] Load Balancer
- [ ] Circuit Breaker (Resilience4j, Hystrix)
- [ ] Message Queue (RabbitMQ, Kafka) para comunicação assíncrona
- [ ] Containerização (Docker, Docker Compose)
- [ ] Orquestração de containers (Kubernetes)
- [ ] Monitoramento e métricas (Prometheus, Grafana)
- [ ] Tracing distribuído (Jaeger, Zipkin)
- [ ] Cache distribuído (Redis)
- [ ] Rate limiting
- [ ] API versioning
- [ ] Testes unitários e de integração

## 📚 Estrutura de Arquivos

```
SBA/
├── frontend/               # Interface Web
│   ├── index.html         # Página principal
│   ├── style.css          # Estilos CSS
│   └── script.js          # Lógica JavaScript
├── gateway.py              # API Gateway (porta 8000) + servidor web
├── users_service.py        # Users Microservice (porta 8001)
├── orders_service.py       # Orders Microservice (porta 8002)
├── billing_service.py      # Billing Microservice (porta 8003)
├── test_client.py          # Cliente de teste/demonstração (CLI)
├── run_all.sh              # Script para iniciar todos os serviços
├── requirements.txt        # Dependências Python
├── README.md              # Esta documentação
├── CLAUDE.md              # Documentação para Claude Code
├── main.py                # Implementação original (monolítica)
└── logs_*.log             # Arquivos de log (gerados em runtime)
```

## 🐛 Troubleshooting

### Erro "Address already in use"
```bash
# Encontrar processo na porta
lsof -ti:8000

# Matar processo
kill -9 $(lsof -ti:8000)
```

### Serviços não respondem
1. Verifique se todos os serviços estão rodando
2. Consulte os logs: `tail -f logs_*.log`
3. Teste health check: `curl http://localhost:8000/health`

### Dependências não encontradas
```bash
pip install -r requirements.txt --upgrade
```

## 👨‍💻 Desenvolvimento

Este projeto foi desenvolvido como uma demonstração educacional de arquitetura de microserviços, implementando os conceitos fundamentais de:

- Decomposição de aplicação em serviços
- Comunicação entre serviços
- API Gateway como ponto de entrada
- Orquestração de fluxos complexos

## 📄 Licença

Este é um projeto educacional desenvolvido para fins de demonstração e aprendizado.

---

**Desenvolvido com Python, FastAPI e muito ☕**
