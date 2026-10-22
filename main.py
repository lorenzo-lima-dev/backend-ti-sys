from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI, Request


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(
        host= "127.0.0.1",
        port="5432",
        database="gabardo",
        user="postgres",
        password="##ççGabardo!1",
        min_size=10,
        max_size=30,
        command_timeout=10,
    )
    try:
        yield
    finally:
        await app.state.pool.close()


app = FastAPI(lifespan=lifespan)