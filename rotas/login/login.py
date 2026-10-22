from fastapi import APIRouter
from utils.senha_hash import hash_senha, verificar_senha

router = APIRouter(prefix="/tecnicos", tags=["Técnicos"])


@router.get("/")
async def get_tecnicos():
    