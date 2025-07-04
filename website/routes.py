from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, OAuth2Client
from database import get_db


router = APIRouter(prefix='/home')

templates = Jinja2Templates(directory="templates")


# вместо встроенных сессией flask необходимо использовать библиотеку fastapi-sessions
async def current_user(db: AsyncSession = Depends(get_db)):
    if 'id' in request.session:
        uid = request.session['id']
        return await db.execute(select(User)).first()
    return None


@router.get('/', response_class=HTMLResponse)
async def get_home(request: Request, db: AsyncSession = Depends(get_db)):
    user = await current_user()
    if user:
        clients = await db.execute(select(OAuth2Client).filter_by(user_id=user.id))
    else:
        clients = []

    return templates.TemplateResponse('home.html', {"request" : request})


@router.post('/')
async def create_home(db: AsyncSession = Depends(get_db)):
    username = request.form.get('username')
    user = await db.execute(select(User).filter_by(username=username)).first()
    if not user:
        user = User(username=username)
        db.add(user)
        await db.commit()
    request.session['id'] = user.id
    next_page = request.args.get('next')
    if next_page:
        return redirect(next_page)
    return redirect('/')


@router.get('/logout')
def logout():
    del session['id']
    return RedirectResponse('/home')
