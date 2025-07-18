from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db
from routes import router
from oauth2 import config_oauth
import uvicorn

from starsessions import CookieStore, SessionAutoloadMiddleware, SessionMiddleware

from website.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


settings = Settings(SECRET_KEY="SECRET_KEY")

app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionAutoloadMiddleware)
app.add_middleware(SessionMiddleware, store=CookieStore(secret_key="key"))
app.include_router(router)
config_oauth(app, settings)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
