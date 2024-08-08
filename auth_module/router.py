from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import timedelta
from database import get_db
from auth_module.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth_module import crud, schemas, models
from fastapi import APIRouter, Depends, Form, Request

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("auth_module/register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Проверяем, существует ли пользователь с таким именем
    db_user = crud.get_user_by_username(db, username=username)
    if db_user:
        return templates.TemplateResponse("auth_module/register.html", {"request": request, "error": "Username already registered"})

    # Проверяем, существует ли пользователь с таким email
    db_email_user = crud.get_user_by_email(db, email=email)  # Предполагаем, что эта функция определена
    if db_email_user:
        return templates.TemplateResponse("auth_module/register.html", {"request": request, "error": "Email already registered"})

    # Проверяем правильность email с помощью Pydantic
    try:
        valid_email = schemas.UserCreate(username=username, email=email, password=password).email
    except ValueError:
        return templates.TemplateResponse("auth_module/register.html", {"request": request, "error": "Invalid email address"})

    # Создаем нового пользователя
    user = schemas.UserCreate(username=username, email=valid_email, password=password)
    try:
        crud.create_user(db=db, user=user)
    except Exception:
        return templates.TemplateResponse("auth_module/register.html", {"request": request, "error": "Error while creating user"})

    return templates.TemplateResponse("auth_module/login.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request, error: str = None):
    return templates.TemplateResponse("auth_module/login.html", {"request": request, "error": error})


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None
):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return RedirectResponse(url=f"/login?error=Invalid credentials", status_code=303)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Устанавливаем токен в куки
    response = RedirectResponse(url="/rooms", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return response
