"""
Users Microservice
Porta: 8001
Responsabilidades: Gerenciamento de usuários (criar, autenticar, buscar)
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Dict, Optional
import uvicorn
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[USERS-SERVICE] %(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Users Service", version="1.0.0", docs_url=None, redoc_url=None)

# Armazenamento em memória
USERS_DB: Dict[int, dict] = {}
USERS_BY_EMAIL: Dict[str, int] = {}
NEXT_USER_ID = 1

# Modelos Pydantic
class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str

# Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "users"}

@app.post("/users/create", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """Criar novo usuário"""
    global NEXT_USER_ID

    logger.info(f"Criando usuário: {user.email}")

    # Verificar se email já existe
    if user.email in USERS_BY_EMAIL:
        logger.warning(f"Email já existe: {user.email}")
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Criar usuário
    user_id = NEXT_USER_ID
    NEXT_USER_ID += 1

    user_data = {
        "user_id": user_id,
        "name": user.name,
        "email": user.email
    }

    USERS_DB[user_id] = user_data
    USERS_BY_EMAIL[user.email] = user_id

    logger.info(f"Usuário criado com sucesso: ID={user_id}")
    return user_data

@app.post("/users/login", response_model=UserResponse)
async def login_user(credentials: UserLogin):
    """Autenticar usuário por email"""
    logger.info(f"Tentativa de login: {credentials.email}")

    user_id = USERS_BY_EMAIL.get(credentials.email)

    if not user_id:
        logger.warning(f"Usuário não encontrado: {credentials.email}")
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user_data = USERS_DB[user_id]
    logger.info(f"Login bem-sucedido: ID={user_id}")
    return user_data

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Buscar usuário por ID"""
    logger.info(f"Buscando usuário: ID={user_id}")

    user_data = USERS_DB.get(user_id)

    if not user_data:
        logger.warning(f"Usuário não encontrado: ID={user_id}")
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    logger.info(f"Usuário encontrado: ID={user_id}")
    return user_data

@app.get("/users")
async def list_users():
    """Listar todos os usuários"""
    logger.info(f"Listando {len(USERS_DB)} usuários")
    return {"users": list(USERS_DB.values()), "total": len(USERS_DB)}

if __name__ == "__main__":
    logger.info("Iniciando Users Service na porta 8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
