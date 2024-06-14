import random
from typing import Annotated
from werkzeug.security import generate_password_hash, check_password_hash

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

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
    Обработчик html страницы подтверждения регистрации кодом.

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


@app_auth.get("/verification", response_class=HTMLResponse)
async def template_verification(request: Request) -> HTMLResponse:
    """
    Обработчик html страницы подтверждения авторизации кодом.

    return:
        Возвращает отрендареный шаблон
    """
    return templates.TemplateResponse(
        "verification/verification.html", {"request": request})


@app_reg.post("/")
async def registration(request: Request,
                       email: Annotated[str, Form()],
                       login: Annotated[str, Form()],
                       password: Annotated[str, Form()],
                       password_two: Annotated[str, Form()]
                       ) -> JSONResponse:
    """
    Обработка логики регистрации.

    args:
        user_log: Получение юзера по логину
        user_mail: Получение юзера по почте
    return:
        Возвращает JSONResponse ответ.
    """
    user_log = await select_by_user(login)
    user_mail = await select_by_email(email)
    # Проверка базы данных на наличие пользователя
    if user_log or user_mail:
        return JSONResponse(
            content={"message": "Пользователь с таким логином или почтой, уже существует!"},
            status_code=400)
    # Создание одноразового кода
    code = random.randint(1000, 9999)
    # Передача в сессию данных формы
    request.session['email'] = email
    request.session['login'] = login
    request.session['password'] = password
    request.session['code'] = code
    try:
        with open('template_message/t_code.txt',
                  'r', encoding='utf-8') as file:
            content = file.read()
        # Отправка кода на указанную почту
        await send_email(email, content, {'code': code})
        # Возврат положительного результата (кода 200), для редиректа
        return JSONResponse(content={"key": email},
                            status_code=200)
    except Exception as ex:
        return JSONResponse(content={"message": ex},
                            status_code=400)


@app_reg.post("/confirm")
async def confirm(request: Request,
                  code: Annotated[str, Form()]) -> JSONResponse:
    """
    Подтверждение регистрации, по введенному коду.

    Сессия очищается после 3х минут, если код вводится не верный.

    args:
        email: почта из сессии из формы registration-form
        login: Логин из сессии из формы registration-form
        password: Пароль из сессии из формы registration-form
        verification_code: Код из сессии, созданый в пред. функции
    return:
        Возвращает JSONResponse ответ.
    """
    # Получение данных из сессии
    email = request.session.get('email')
    login = request.session.get('login')
    password = request.session.get('password')
    verification_code = request.session.get('code')
    # Проверка введённого кода с кодом, полученным из сессии
    if str(code) == str(verification_code):
        # Добавление пользователя в базу данных
        await add_user(email, login, generate_password_hash(password))
        # Очистка сессии
        request.session.clear()
        return JSONResponse(content={"message": "Введенный код верный!"},
                            status_code=200)
    else:
        return JSONResponse(content={"message": "Введенный код неверный!"},
                            status_code=400)


@app_auth.post("/")
async def authorization(request: Request,
                        login: Annotated[str, Form()],
                        password: Annotated[str, Form()]
                        ) -> JSONResponse:
    """
    Обработчик логики авторизации.

    args:
        user: Пользователь из базы данных
        code: Сгенерированный одноразовый код
    return:
        Возвращает JSONResponse ответ.
    """
    if "@" in login:
        user = await select_by_email(login)
    else:
        user = await select_by_user(login)
    if not user or not check_password_hash(user[0].password, password):
        return JSONResponse(content={"message": "Неверный логин или пароль!"},
                            status_code=400)
    else:
        code = random.randint(1000, 9999)
        request.session['code'] = code
        try:
            with open('template_message/t_pass.txt',
                      'r', encoding='utf-8') as file:
                content = file.read()
            await send_email(user[0].email, content, {'code': code})
            return JSONResponse(content={"key": user[0].email},
                                status_code=200)
        except Exception as ex:
            return JSONResponse(content={"message": ex},
                                status_code=400)


@app_auth.post("/verification")
async def verification(request: Request,
                       code: Annotated[str, Form()]) -> JSONResponse:
    """
    Функция подтверждения авторизации, по введенному коду.

    Сессия очищается после 3х минут, если код вводится не верный.

    args:
        verification_code: Код полученный из сессии.

    return:
        Возвращает JSONResponse ответ.
    """
    verification_code = request.session.get('code')

    if str(code) == str(verification_code):
        request.session.clear()
        return JSONResponse(content={"message": "Авторизация удалась!"},
                            status_code=200)
    else:
        return JSONResponse(content={"message": "Введенный код неверный!"},
                            status_code=400)
