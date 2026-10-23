import jwt
import os
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, APIKeyHeader, HTTPAuthorizationCredentials

API_KEY_NAME = "ÇÇççKEYGAB"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

CHAVE_SECRETA_INVENTARIO = os.getenv("API_KEY_INVENTARIO", "chave_mestra_ti_sys_2026")
SECRET_KEY = os.getenv("JWT_SECRET", "uma_chave_super_longa_e_impossivel_de_adivinhar")
ALGORITHM = "HS256"
security = HTTPBearer()

def criar_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=2)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def validar_api_key(api_key: str = Security(api_key_header)):
    if api_key != CHAVE_SECRETA_INVENTARIO:
        raise HTTPException(status_code=401, detail="Acesso negado: Chave de API inválida.")
    return api_key

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