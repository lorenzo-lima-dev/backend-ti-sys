from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.conn import iniciar_pool, fechar_pool

from rotas.inventario import inventario

@asynccontextmanager
async def lifespan(app: FastAPI):
    await iniciar_pool()
    yield
    await fechar_pool()

app = FastAPI(
    title="Backend TI Sys",
    description="API para recebimento de dados pesados e gestão de chamados",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(inventario.router)