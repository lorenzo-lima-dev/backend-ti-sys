from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_hash(senha_plana: str) -> str:
    return pwd_context.hash(senha_plana)

def verificar_senha(senha_plana: str, hash_salvo: str) -> bool:
    return pwd_context.verify(senha_plana, hash_salvo)