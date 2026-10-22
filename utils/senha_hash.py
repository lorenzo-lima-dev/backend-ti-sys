import asyncio
import bcrypt

async def hash_senha(senha: str, rounds: int = 12) -> bytes:
    return await asyncio.to_thread(
        bcrypt.hashpw,
        senha.encode("utf-8"),
        bcrypt.gensalt(rounds=rounds)
    )

async def verificar_senha(senha: str, hash_senha: bytes) -> bool:
    return await asyncio.to_thread(
        bcrypt.checkpw,
        senha.encode("utf-8"),
        hash_senha
    )