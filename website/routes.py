import time

from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Users, OAuth2Client
from database import get_db
from werkzeug.security import gen_salt
from oauth2 import authorization


router = APIRouter(prefix='/home')

templates = Jinja2Templates(directory="templates")


def split_by_crlf(s):
    return [v for v in s.splitlines() if v]

async def current_user(request: Request, db: AsyncSession):
    if 'id' in request.session:
        user_id = request.session['id']
        return await db.scalar(select(Users).where(Users.id == user_id))
    return None


@router.get('/', response_class=HTMLResponse)
async def get_home(request: Request, db: AsyncSession = Depends(get_db)):
    user = await current_user(request, db)
    if user:
        clients = await db.execute(select(OAuth2Client).filter_by(user_id=user.id))
    else:
        clients = []

    return templates.TemplateResponse('home.html', {"request" : request, "clients": clients})


@router.post('/')
async def create_home(request: Request, username: str = Form(), db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(Users).where(Users.username == username))
    if not user:
        user = Users(username=username)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    request.session['id'] = user.id
    next_page = request.query_params.get('next')
    if next_page:
        return RedirectResponse(next_page)
    return RedirectResponse('/')


@router.get('/logout')
def logout(request: Request):
    del request.session['id']
    return RedirectResponse('/')


@router.get('/create_client')
async def get_client(request: Request, db: AsyncSession = Depends(get_db)):
    user = await current_user(request, db)
    if not user:
        return RedirectResponse('/')
    return templates.TemplateResponse('create_client.html', {"request" : request})


@router.post('/create_client')
async def create_client(request: Request, client_name=Form(), client_uri=Form(), grant_type=Form(), redirect_uri=Form(), response_type=Form(), scope=Form(), token_endpoint_auth_method=Form(), db: AsyncSession = Depends(get_db)):
    user = await current_user(request, db)
    if not user:
        return RedirectResponse('/')

    client = OAuth2Client(
        client_id=gen_salt(24),
        client_id_issued_at=int(time.time()),
        user_id=user.id,
    )

    form_data = {
        "client_name": client_name,
        "client_uri": client_uri,
        "grant_types": split_by_crlf(grant_type),
        "redirect_uris": split_by_crlf(redirect_uri),
        "response_types": split_by_crlf(response_type),
        "scope": scope,
        "token_endpoint_auth_method": token_endpoint_auth_method
    }

    client.set_client_metadata(form_data)

    if form_data.get('token_endpoint_auth_method') == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)

    db.add(client)
    await db.commit()
    return RedirectResponse('/')


@router.post('/oauth/token')
async def issue_token(request: Request):
    return authorization.create_token_response(request)