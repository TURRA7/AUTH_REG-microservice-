import random
from typing import Annotated
from werkzeug.security import generate_password_hash, check_password_hash

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from config import SESSION_STATE_CODE, SESSION_STATE_MAIL
from database.FDataBase import (select_by_user, select_by_email,
                                add_user, update_password)
from e_mails.send_letters import send_email


# Указываем папку для чтения html шаблонов
templates = Jinja2Templates(directory="templates")
# Роутеры, для формы регистрации
app_reg = APIRouter(prefix="/registration")
# Роутеры, для формы авторизации
app_auth = APIRouter(prefix="/authorization")
# Роутеры для логаута
app_logout = APIRouter(prefix="/logout")


@app_reg.get("/", response_class=HTMLResponse)
async def template_reg(request: Request) -> HTMLResponse:
    """
    Обработчик html шаблона регистрации.

    return:
        Возвращает отрендареный шаблон
    """
    return templates.TemplateResponse("reg/reg.html", {"request": request})


@app_reg.get("/confirm", response_class=HTMLResponse)
async def template_confirm(request: Request) -> HTMLResponse:
    """
    Обработчик html шаблона ввода кода для регистрации.

    return:
        Возвращает отрендареный шаблон
    """
    return templates.TemplateResponse(
        "confirm/confirm.html", {"request": request})


@app_auth.get("/", response_class=HTMLResponse)
async def template_auth(request: Request) -> HTMLResponse:
    """
    Обработчик html шаблона авторизации.

    return:
        Возвращает отрендареный шаблон
    """
    return templates.TemplateResponse("auth/auth.html", {"request": request})


@app_auth.get("/verification", response_class=HTMLResponse)
async def template_verification(request: Request) -> HTMLResponse:
    """
    Обработчик html шаблона ввода кода для авторизации.

    return:
        Возвращает отрендареный шаблон
    """
    return templates.TemplateResponse(
        "verification/verification.html", {"request": request})


@app_auth.get("/recover", response_class=HTMLResponse)
async def template_recover(request: Request) -> HTMLResponse:
    """
    Обработчик html шаблона восстановления пароля(указание почты).

    return:
        Возвращает отрендареный шаблон
    """
    return templates.TemplateResponse(
        "recover/recover.html", {"request": request})


@app_auth.get("/recover/reset_code", response_class=HTMLResponse)
async def template_reset_code(request: Request) -> HTMLResponse:
    """
    Обработчик html шаблона восстановления пароля(ввод кода с почты).

    return:
        Возвращает отрендареный шаблон
    """
    return templates.TemplateResponse(
        "reset_code/reset_code.html", {"request": request})


@app_auth.get("/recover/reset_code/change_password",
              response_class=HTMLResponse)
async def template_change_password(request: Request) -> HTMLResponse:
    """
    Обработчик html шаблона восстановления пароля(ввод нового пароля).

    return:
        Возвращает отрендареный шаблон
    """
    return templates.TemplateResponse(
        "change_password/change_password.html", {"request": request})


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
        code: Сгенерированный 4х значный код
        email, login, password, password_two: данные из формы
        *password, password_two(пароль/повтор пароля)

    return:
        1. Получаем юзера по почте user_mail и логину user_log,
        2. Проверяем наличие юзера БД.
        3. Если пользователь присутствует:
        В состояния сессии, передаётся: email, login, password,
        code(одноразовый 4х значный код). В блоке try - выполняется получение
        шаблона, далее на указаную почту, отправляется код(code) и возвращается
        соответствующий JSONResponse ответ.
    """
    user_log = await select_by_user(login)
    user_mail = await select_by_email(email)
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
    """
    Подтверждение регисcodeз формы.
        password: Пароль из формы.
        verification_code: Код из сессии, созданый в функции registration
        code: данные из формы

    return:
        1. Получаются данные из сессии
        2. Проверка введённого кода с кодом сохранённым в сессии
        3. Добавление пользователя в базу данных функцией
        add_user(пароль с помощью generate_password_hash() передаётся
        в виде хэша)
        4. Очистка сессии
        5. Передача соответствующего JSONResponse ответа
    """
    email = request.session.get('email')
    login = request.session.get('login')
    password = request.session.get('password')
    verification_code = request.session.get('code')
    if str(code) == str(verification_code):
        await add_user(email, login, generate_password_hash(password))
        request.session.clear()
        return JSONResponse(content={"message": "Введенный код верный!"},
                            status_code=200)
    else:
        return JSONResponse(content={"message": "Введенный код неверный!"},
                            status_code=400)


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
        1. Присваиваем переменной user, результат получения данных из БД,
        в зависимости от того, введён логин или почта
        2. Далее проверяем, соответствует ли пароль, указанному пользователю
        3. Если указывает, создаём и сохраняем 4х значный код (code) в сессии
        4. Отправляет код(code) на почту пользователя по шаблону t_pass.txt
        5. Устанавливаем в response JSONResponse ответ, а так же присваиваем
        куки, если значение 'запомнить меня'(remember_me) задействовано,
        возврашаем ответ с куками.
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
            response = JSONResponse(content={"key": user[0].email},
                                    status_code=200)
            if remember_me:
                # Устанавливаем cookie для запоминания пользователя
                response.set_cookie(key="remember_me", value="true",
                                    max_age=30*24*60*60)
                # Здесь логика запоминания например, через JWT токены и т.д.
            return response
        except Exception as ex:
            return JSONResponse(content={"message": str(ex)},
                                status_code=400)


@app_auth.post("/verification")
async def verification(request: Request,
                       code: Annotated[str, Form()]) -> JSONResponse:
    """
    Функция подтверждения авторизации, по введенному коду.

    Сессия очищается после 6х минут, если код вводится не верный.

    args:
        verification_code: Код полученный из сессии.
        code: Данные из формы

    return:
        1. Получаем код(verification_code) из сессии
        2. Сверяем код из сессии, с введённым в форме (code)
        3. Если код верный, очищаем сессию, производим аутентификацию
        и атворизацию
        4. Если код неверный, возвращаем соответствующий JSONResponse ответ
    """
    verification_code = request.session.get('code')

    if str(code) == str(verification_code):
        request.session.clear()
        return JSONResponse(content={"message": "Авторизация удалась!"},
                            status_code=200)
    else:
        return JSONResponse(content={"message": "Введенный код неверный!"},
                            status_code=400)


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
