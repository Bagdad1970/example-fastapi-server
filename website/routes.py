from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User, OAuth2Client
from database import get_db


router = APIRouter(prefix='/home')

templates = Jinja2Templates(directory="templates")


async def current_user(request: Request, db: AsyncSession = Depends(get_db)):
    if 'id' in request.session:
        uid = request.session['id']
        return await db.execute(select(User).where(User.id == user_id))
    return None


@router.get('/', response_class=HTMLResponse)
async def get_home(request: Request, db: AsyncSession = Depends(get_db)):
    user = await current_user(request)
    print(user)
    if user:
        clients = await db.execute(select(OAuth2Client).filter_by(user_id=user.id))
    else:
        clients = []

    return templates.TemplateResponse('home.html', {"request" : request})


@router.post('/')
async def create_home(request: Request, username: str = Form(), db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.username == username))
    if not user:
        user = User(username=username)
        db.add(user)
        await db.commit()
    print(user)
    request.session['id'] = user.id
    next_page = request.args.get('next')
    if next_page:
        return redirect(next_page)
    return redirect('/')


@router.get('/logout')
def logout(request: Request):
    del request.session['id']
    return RedirectResponse('/home')
