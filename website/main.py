from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db, get_db
from routes import router
import uvicorn

from starsessions import CookieStore, SessionAutoloadMiddleware, SessionMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionAutoloadMiddleware)
app.add_middleware(SessionMiddleware, store=CookieStore(secret_key="key"))
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
