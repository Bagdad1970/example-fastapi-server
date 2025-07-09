from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User, OAuth2Client
from database import get_db


router = APIRouter(prefix='/home')

templates = Jinja2Templates(directory="templates")


async def current_user(request: Request, db: AsyncSession):
    if 'id' in request.session:
        user_id = request.session['id']
        return await db.scalar(select(User).where(User.id == user_id))
    return None


@router.get('/', response_class=HTMLResponse)
async def get_home(request: Request, db: AsyncSession = Depends(get_db)):
    user = await current_user(request, db)
    if user:
        clients = await db.execute(select(OAuth2Client).filter_by(user_id=user.id))
    else:
        clients = []

    return templates.TemplateResponse('home.html', {"request" : request})


@router.post('/')
async def create_home(request: Request, username: str = Form(), db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.username == username))
    if not user:
        user = User(username=username)
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
