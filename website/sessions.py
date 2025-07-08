import datetime
import typing

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse, RedirectResponse

from starsessions import CookieStore, SessionAutoloadMiddleware, SessionMiddleware

app = FastAPI()
app.add_middleware(SessionAutoloadMiddleware)
app.add_middleware(SessionMiddleware, store=CookieStore(secret_key="key"))
