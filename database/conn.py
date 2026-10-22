import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

# Variável global que vai guardar nosso Pool de conexões TCP
pool = None

async def iniciar_pool():
    global pool
    # O min_size e max_size definem quantas conexões simultâneas ficam abertas no SO.
    # 50 é o suficiente para triturar milhares de requests por segundo em concorrência.
    pool = await asyncpg.create_pool(
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGNAME"),
        host=os.getenv("PGHOST", "127.0.0.1"),
        min_size=10,
        max_size=50
    )
    print("Connection Pool com asyncpg ligado na veia!")

async def fechar_pool():
    global pool
    if pool:
        await pool.close()
        print("Connection Pool encerrado.")

async def get_db():
    # Injetor de dependência para o FastAPI pegar uma conexão do pool
    async with pool.acquire() as connection:
        yield connection