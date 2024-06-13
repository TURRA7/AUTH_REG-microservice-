import random
from typing import Annotated
from werkzeug.security import generate_password_hash, check_password_hash

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from database.FDataBase import select_by_user, select_by_email, add_user
from e_mails.send_letters import send_email


# Указываем папку для чтения html шаблонов
templates = Jinja2Templates(directory="templates")
# Регистрируем роутеры, для формы регистрации
app_reg = APIRouter(prefix="/registration")
# Регистрируем роутеры, для формы авторизации
app_auth = APIRouter(prefix="/authorization")


@app_reg.get("/", response_class=HTMLResponse)
async def template_reg(request: Request) -> HTMLResponse:
    """
    Обработчик html страницы регистрации.

    return:
        Возвращает отрендареный шаблон
    """
    return templates.TemplateResponse("reg/reg.html", {"request": request})


@app_reg.get("/confirm", response_class=HTMLResponse)
async def template_confirm(request: Request) -> HTMLResponse:
    """
    Обработчик html страницы подтверждения кода.

    return:
        Возвращает отрендареный шаблон
    """
    return templates.TemplateResponse(
        "confirm/confirm.html", {"request": request})


@app_auth.get("/", response_class=HTMLResponse)
async def template_auth(request: Request) -> HTMLResponse:
    """
    Обработчик html страницы авторизации.

    return:
        Возвращает отрендареный шаблон
    """
    return templates.TemplateResponse("auth/auth.html", {"request": request})


@app_reg.post("/")
async def registration(request: Request,
                       email: Annotated[str, Form()],
                       login: Annotated[str, Form()],
                       password: Annotated[str, Form()],
                       password_two: Annotated[str, Form()]
                       ) -> JSONResponse:
    """
    Данная функция обрабатывает логику регистрации.

    args:
        user_log: Получение юзера по логину
        user_mail: Получение юзера по почте
    """
    user_log = await select_by_user(login)
    user_mail = await select_by_email(email)
    # Проверка базу данных на наличие пользователя
    if user_log or user_mail:
        return JSONResponse(
            content={"message": "Пользователь с таким логином или почтой, уже существует!"},
            status_code=400)

    code = random.randint(1000, 9999)
    request.session['email'] = email
    request.session['login'] = login
    request.session['password'] = password
    request.session['code'] = code
    try:
        with open('template_message/t_code.txt',
                  'r', encoding='utf-8') as file:
            content = file.read()
        await send_email(email, content, {'code': code})
        return JSONResponse(content={"key": email},
                            status_code=200)
    except Exception as ex:
        return JSONResponse(content={"message": ex},
                            status_code=400)


@app_reg.post("/confirm")
async def confirm(request: Request,
                  code: Annotated[str, Form()]) -> JSONResponse:
    email = request.session.get('email')
    login = request.session.get('login')
    password = request.session.get('password')
    verification_code = request.session.get('code')
    if str(code) == str(verification_code):
        await add_user(email, login, generate_password_hash(password))
        request.session.clear()
        return RedirectResponse(url="/authorization")
    else:
        request.session.clear()
        return JSONResponse(content={"message": "Введенный код неверный!"},
                            status_code=400)
    # Доработать функцию, она при редиректе на authorization, почему-то ожидает поля login и password, надо это исправить!


@app_auth.post("/")
async def authorization(request: Request,
                        login: Annotated[str, Form()],
                        password: Annotated[str, Form()]
                        ) -> JSONResponse:
    """
    Данная функция обрабатывает логику авторизации.

    args:
        ...
    """
    if "@" in login:
        user = await select_by_email(login)
    else:
        user = await select_by_user(login)
    if not user or not check_password_hash(user[0].password, password):
        return JSONResponse(content={"message": "Неверный логин или пароль!"},
                            status_code=400)
    else:
        return JSONResponse(content={"message": "Авторизация успешна!"},
                            status_code=200)
