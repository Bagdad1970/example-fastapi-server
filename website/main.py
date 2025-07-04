from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db, get_db
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router)
