import random
from typing import Annotated
from werkzeug.security import generate_password_hash, check_password_hash

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache

from backend.backend import Authorization, Registration
from config import SESSION_STATE_CODE, SESSION_STATE_MAIL
from database.FDataBase import (select_by_user, select_by_email,
                                add_user, update_password)
from backend.backend import send_email
from link_backend_frontend.link_BF import TemplateHandler


# Роутеры, для формы регистрации
app_reg = APIRouter(prefix="/registration")
# Роутеры, для формы авторизации
app_auth = APIRouter(prefix="/authorization")
# Роутеры для логаута
app_logout = APIRouter(prefix="/logout")


# Маршруты класса TemplateHandler(позже не вносить в репозиторий с API):
registration_handler = TemplateHandler(
    router=app_reg, route="/", template_path="reg/reg.html")
confirm_handler = TemplateHandler(
    router=app_reg, route="/confirm", template_path="confirm/confirm.html")
authorization_handler = TemplateHandler(
    router=app_auth, route="/", template_path="auth/auth.html")
verification_handler = TemplateHandler(
    router=app_auth, route="/verification",
    template_path="verification/verification.html")
recover_handler = TemplateHandler(
    router=app_auth, route="/recover", template_path="recover/recover.html")
reset_code_handler = TemplateHandler(
    router=app_auth, route="/recover/reset_code",
    template_path="reset_code/reset_code.html")
change_password_handler = TemplateHandler(
    router=app_auth, route="/recover/reset_code/change_password",
    template_path="change_password/change_password.html")


@app_reg.post("/")
async def registration(request: Request,
                       email: Annotated[str, Form()],
                       login: Annotated[str, Form()],
                       password: Annotated[str, Form()],
                       password_two: Annotated[str, Form()]
                       ) -> JSONResponse:
    """
    Обработка регистрации.

    args:
        result: Обработка пользователя: добавление в БД,
        отправка кода на почту

    return:
        Возвращает готовый JSONResponse ответ с
        состоянием добавления пользователя
    """
    result = await Registration.register(email, login, password)
    request.session['email'] = email
    request.session['login'] = login
    request.session['password'] = password
    request.session['code'] = result['code']
    return JSONResponse(content={"key": result["email"]}, status_code=200)


@app_reg.post("/confirm")
async def confirm(request: Request,
                  code: Annotated[str, Form()]) -> JSONResponse:
    """
    Обработка формы ввода 'кода подтверждения регистрации'.

    args:
        email, login, password, verification_code: Данные из сессии
        добавленные в на шаге регистрации
        result: Обработка ввода и подтверждение кода

    return:
        Возвращает готовый JSONResponse ответ с
        состоянием добавления пользователя
    """
    email = request.session.get('email')
    login = request.session.get('login')
    password = request.session.get('password')
    verification_code = request.session.get('code')
    result = await Registration.confirm_register(
        email, login, password, code, verification_code)
    if result['status_code'] == 200:
        request.session.clear()
        response = JSONResponse(content={"message": result["message"]},
                                status_code=200)
    else:
        response = JSONResponse(content={"message": result["message"]},
                                status_code=400)
    return response


@app_auth.post("/")
async def authorization(request: Request,
                        login: Annotated[str, Form()],
                        password: Annotated[str, Form()],
                        remember_me: bool = Form(False)
                        ) -> JSONResponse:
    """
    Обработчик логики авторизации.

    args:
        user: Пользователь из базы данных
        code: Сгенерированный 4х значный код
        response: JSONResponse ответ
        login, password: данные из формы
        remember_me: положение флажка 'запомнить меня' в форме

    return:
        Возвращает готовый JSONResponse ответ удачным или неудачным
        статусом авторизации, а так же сохраняет код отправленный на почту
        в сессию и задаёт куки для флага "запомнить меня"
    """
    result = await Authorization.authorization(login, password)
    if result['status_code'] == 200:
        request.session['code'] = result['code']
        response = JSONResponse(content={"key": result["login"]},
                                status_code=200)
    else:
        response = JSONResponse(content={"message": result["message"]},
                                status_code=result['status_code'])
    if remember_me:
        result.set_cookie(key="remember_me", value="true", max_age=30*24*60*60)
    return response


@app_auth.post("/verification")
async def verification(request: Request,
                       code: Annotated[str, Form()]) -> JSONResponse:
    """
    Обработка формы ввода 'кода подтверждения авторизации'.

    args:
        code: Данные из формы
        result: Обработка ввода и подтверждение кода

    return:
        Возвращает готовый JSONResponse ответ с
        состоянием авторизации
    """
    verification_code = request.session.get('code')
    result = await Authorization.confirm_auth(code, verification_code)
    if result['status_code'] == 200:
        request.session.clear()
        response = JSONResponse(content={"message": result["message"]},
                                status_code=result['status_code'])
    else:
        response = JSONResponse(content={"message": result["message"]},
                                status_code=result['status_code'])
    return response


@app_auth.post("/recover")
async def recover(request: Request,
                  user: Annotated[str, Form()]) -> JSONResponse:
    """
    Функция восствновления пароля(ввод почты).

    args:
        result: Пользователь из бады данных
        code: Сгенерированный 4х значный код
        user: Данные из формы (введённая почта)

    return:
        1. Проверяем что введённый данные, являются почтой
        2. Передаём в сессию код сессии, указанный в переменной
        окружения SESSION_STATE_MAIL
        3. Генерируем код(code), передаём в сессию введённую почту
        и пароль
        4. Отправляем на указанную почту код(code) с помощью
        шаблона t_recover.txt
        5. Возвращаем соответствующий JSONResponse ответ.
    """
    if "@" in user:
        result = await select_by_email(user)
        if not result:
            return JSONResponse(
                content={"message": "Пользователь не существует!"},
                status_code=400)
        else:
            try:
                request.session['state'] = SESSION_STATE_MAIL
                code = random.randint(1000, 9999)
                request.session['code'] = code
                request.session['email'] = user
                with open('template_message/t_recover.txt',
                          'r', encoding='utf-8') as file:
                    content = file.read()
                await send_email(user, content, {'code': code})
                return JSONResponse(content={"key": user},
                                    status_code=200)
            except Exception as ex:
                return JSONResponse(content={"message": str(ex)},
                                    status_code=400)
    else:
        return JSONResponse(content={"message": "Укажите почту, а не логин!"},
                            status_code=400)


@app_auth.post("/recover/reset_code")
async def reset_code(request: Request,
                     code: Annotated[str, Form()]) -> JSONResponse:
    """
    Функция восствновления пароля(ввод кода из почты).

    Сессия очищается после 6х минут, если код вводится не верный.

    args:
        verification_code: Код полученный из сессии.
        code: Данные из формы

    return:
        1. Проверяем состояние сессии
        2. Получаем код(verification_code) из сессии и
        сверяем его с кодом(code) введённым пользователем в сессии
        3. Удаялем старое состояние сессии указанное в SESSION_STATE_MAIL
        4. Задаём новое состояние сесиии SESSION_STATE_CODE
        5. Возвращаем JSONResponse ответ
    """
    if request.session.get('state') == SESSION_STATE_MAIL:
        verification_code = request.session.get('code')
        if str(code) == str(verification_code):
            del request.session['state']
            request.session['state'] = SESSION_STATE_CODE
            return JSONResponse(content={"message": "Можете менять пароль!"},
                                status_code=200)
        else:
            return JSONResponse(content={"message": "Введенный код неверный!"},
                                status_code=400)
    else:
        return JSONResponse(content={"message": "Вы не указали почту!"},
                            status_code=400)


@app_auth.post("/recover/reset_code/change_password")
async def change_password(request: Request,
                          password: Annotated[str, Form()],
                          password_two: Annotated[str, Form()]
                          ) -> JSONResponse:
    """
    Функция восствновления пароля(изменение пароля).

    Сессия очищается после 6х минут, если код вводится не верный.

    args:
        verification_code: Код полученный из сессии.
        password: Данные из формы(пароль)
        password_two: Данные из формы(повтор пароля)

    return:
        1. Проверяем состояние сессии
        2. Получаем из сессии почту и изменяем пароль в update_password
        с указанием почты и пароля из формы в виде хэща
        с помощью generate_password_hash(password)
        3. Возвращаем JSONResponse ответ
    """
    if request.session.get('state') == SESSION_STATE_CODE:
        try:
            email = request.session.get('email')
            await update_password(email, generate_password_hash(password))
            request.session.clear()
            return JSONResponse(content={"message": "Пароль обновлён!"},
                                status_code=200)
        except Exception as ex:
            return JSONResponse(content={"message": str(ex)},
                                status_code=400)
    else:
        return JSONResponse(content={"message": "Вы не ввели код!"},
                            status_code=400)


@app_logout.post("/")
async def logout(request: Request) -> JSONResponse:
    """Обработчик выхода пользователя"""
    pass
