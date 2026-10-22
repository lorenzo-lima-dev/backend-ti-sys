import jwt
import os
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.getenv("JWT_SECRET", "uma_chave_super_longa_e_impossivel_de_adivinhar")
ALGORITHM = "HS256"
security = HTTPBearer()

def criar_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=2)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def exigir_permissao(roles_permitidas: list):
    async def verificador(credentials: HTTPAuthorizationCredentials = Security(security)):
        token = credentials.credentials
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            cargo = payload.get("role")
            
            if cargo not in roles_permitidas:
                raise HTTPException(status_code=403, detail="Acesso negado: Cargo insuficiente.")
            
            return payload # Retorna os dados do usuário para a rota usar
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expirado.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token fraudado ou inválido.")
            
    return verificador