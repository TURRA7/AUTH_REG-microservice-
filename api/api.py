import random
from typing import Annotated
from werkzeug.security import generate_password_hash, check_password_hash

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from database.FDataBase import select_by_user, select_by_email, add_user
from e_mails.send_letters import send_email

templates = Jinja2Templates(directory="templates")


app_reg = APIRouter()
app_auth = APIRouter()


@app_reg.get("/registration", response_class=HTMLResponse)
async def template_reg(request: Request) -> HTMLResponse:
    """
    Обработчик html страницы регистрации.

    return:
        Возвращает отрендареный шаблон
    """
    return templates.TemplateResponse("reg/reg.html", {"request": request})


@app_reg.post("/registration")
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

    ### Доделать регистрацию с отправкой письма
    ### Доделать регистрацию с отправкой письма
    ### Доделать регистрацию с отправкой письма
    try:
        with open('template_message/t_code.txt', 'r', encoding='utf-8') as file:
            content = file.read()
        await send_email(email, content, {'code': code})
    except Exception as ex:
        return JSONResponse(content={"message": "Проблема с отправкой письма!"},
                            status_code=400)
    await add_user(email, login, generate_password_hash(password))
    return JSONResponse(
        content={"message": "Регистрация успешна!"}, status_code=200)


@app_auth.get("/authorization", response_class=HTMLResponse)
async def template_auth(request: Request) -> HTMLResponse:
    """
    Обработчик html страницы авторизации.

    return:
        Возвращает отрендареный шаблон
    """
    return templates.TemplateResponse("auth/auth.html", {"request": request})


@app_auth.post("/authorization")
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
