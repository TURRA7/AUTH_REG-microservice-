import json
import redis
import sentry_sdk
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from sentry_sdk.integrations.fastapi import FastApiIntegration

from backend.backend import (Authorization, Logout,
                             PasswordRecovery, Registration)
from config import (SECRET_KEY, SENTRY_DNS, SESSION_STATE_CODE,
                    SESSION_STATE_MAIL)
from jwt_tools.jwt import create_jwt_token
from models.models import (CodeConfirm, PasswordChange,
                           Recover, Token, UserAuth, UserReg)


sentry_sdk.init(
    dsn=SENTRY_DNS,
    integrations=[
        FastApiIntegration(),
    ],
    traces_sample_rate=1.0,
)


# Роутеры, для формы регистрации
app_reg = APIRouter(prefix="/registration")
# Роутеры, для формы авторизации
app_auth = APIRouter(prefix="/authorization")
# Роутеры для логаута
app_logout = APIRouter(prefix="/logout")


# ПОдключение Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)


@app_reg.post("/")
async def registration(data: UserReg) -> JSONResponse:
    """
    Регистрация пользователя.

    Args:

        email: Почта.
        login: Логин.
        password: Пароль.
        password_two: Повтор пароля.

    Returns:

        JSONResponse: Результат регистрации.

        - 200: Успешное подтверждение, возвращает сообщение об успехе.
        - 422: Ошибка валидации, возвращает сообщение об ошибке.
        - Другие коды: Соответствующие сообщения об ошибках и коды статусов.

    Notes:

        1. Валидирует данные пользователя.
        2. Сохраняет временные данные в Redis
        3. Отправляет сгенерированный проверочный код на почту.
    """
    result = await Registration.register(data.email,
                                         data.login,
                                         data.password,
                                         data.password_two)
    if result['status_code'] == 200:
        data_redis = {
            "email": data.email,
            "login": data.login,
            "password": data.password,
        }
        redis_client.set(result['code'], json.dumps(data_redis))
        response = JSONResponse(content={"message": "Введите код с почты!"},
                                status_code=200)
    else:
        sentry_sdk.capture_message(result["message"])
        response = JSONResponse(content={"message": result["message"]},
                                status_code=result["status_code"])
    return response


@app_reg.post("/confirm")
async def confirm(data: CodeConfirm) -> JSONResponse:
    """
    Обработка формы ввода кода подтверждения регистрации.

    Args:

        code: Код из из почты.

    Returns:

        JSONResponse: Результат подтверждения кода.

        - 200: Успешное подтверждение, возвращает сообщение об успехе.
        - 422: Ошибка валидации, возвращает сообщение об ошибке.
        - 400: Ошибка подтверждения, возвращает соответствующее сообщение.

    Notes:

        1. Валидирует данные.
        2. По коду с почты достаёт данные из Redis.
        3. сохраняет пользователя в базу данных.
        * Пароль сохраняется в виде хэша.
        4. Очищает Redis от временных данных.
    """
    if not redis_client.exists(data.code):
        return JSONResponse(
            content={"message": "Введённый код не верный!"},
            status_code=400)
    user_data = redis_client.get(data.code)
    user_data = json.loads(user_data.decode('utf-8'))
    if isinstance(user_data, JSONResponse):
        return user_data
    email = user_data.get('email')
    login = user_data.get('login')
    password = user_data.get('password')

    result = await Registration.confirm_register(
        email, login, password)

    if result['status_code'] == 200:
        redis_client.delete(f"login:{data.code}")
        return JSONResponse(content={"message": result["message"]},
                            status_code=200)
    else:
        return JSONResponse(content={"message": result["message"]},
                            status_code=400)


@app_auth.post("/")
async def authorization(data: UserAuth) -> JSONResponse:
    """
    Обработчик логики авторизации.

    !!! поменять доку после исправления функции!!!
    Args:
        login: Логин пользователя,
        password: Пароль пользователя,
        memorize_user: Булево значение(запомнить пользователя).
    Returns:
        JSONResponse: Результат авторизации.
        - 200: Успешная авторизация, возвращает ключ 'key' (login).
        - Другие коды: Соответствующие сообщения об ошибках и коды статусов.
    Notes:
        - Сохраняет код, отправленный на почту, и логин в сессию.
        - Если установлен флажок 'запомнить меня',
        устанавливает соответствующую куку.
    """
    result = await Authorization.authorization(data.login,
                                               data.password)
    if result['status_code'] == 200:
        data_redis = {
            "code": result['code'],
            "login": data.login,
            "remember_user": data.memorize_user
        }
        redis_client.set(result['code'], json.dumps(data_redis))
        response = JSONResponse(content={"key": result["login"]},
                                status_code=200)
    else:
        response = JSONResponse(content={"message": result["message"]},
                                status_code=result['status_code'])
    return response


@app_auth.post("/verification")
async def verification(data: CodeConfirm) -> JSONResponse:
    """
    Обработка формы ввода кода подтверждения авторизации.

    !!! поменять доку после исправления функции!!!
    Args:
        data: Код из почты и юзер(логин/почта. в зависимости от того,
        что было передано в предыдущем шаге /authorization).
    Returns:
        JSONResponse: Результат подтверждения кода.
        - 200: Успешное подтверждение, возвращает сообщение и токен,
        очищает сессию.
        - 422: Ошибка валидации, возвращает сообщение об ошибке.
        - Другие коды: Соответствующие сообщения об ошибках и коды статусов.
    Notes:
        - Получает код и логин из сессии, передаёт на бэкенд, при успешном
        ответе с бэкенда, очищает сессию.
    """

    if not redis_client.exists(data.code):
        response = JSONResponse(
            content={"message": "Введённый код не верный!"},
            status_code=400)
    user_data = redis_client.get(data.code)
    user_data = json.loads(user_data.decode('utf-8'))
    if isinstance(user_data, JSONResponse):
        return user_data
    login = user_data.get('login')
    auth_code = user_data.get('code')

    # Вот тут надо докрутить авторизацию!!!
    token = create_jwt_token(login=login,
                             token_lifetime_hours=1,
                             secret_key=SECRET_KEY)
    headers = {"Authorization": f"Bearer {token}"}
    response = JSONResponse(content={"message": "Вы авторизированны!"},
                            headers=headers,
                            status_code=200)
    redis_client.delete(f"login:{auth_code}")
    return response


@app_auth.post("/recover")
async def recover(data: Recover) -> JSONResponse:
    """
    Обработчик логики восстановления (изменения) пароля.

    Args:

        user: Логин или почта введённая пользователем.

    Returns:

        JSONResponse: Результат восстановления пароля.

        - 200: Успешное подтверждение, возвращает сообщение об успехе.
        - 422: Ошибка валидации, возвращает сообщение об ошибке.
        - Другие коды: Соответствующие сообщения об ошибках и коды статусов.

    Notes:

        1. Валидирует данные
        2. По введённыи данным находит пользователя и отправляет на почту
        сгенерированный код.
        3. Сохраняет в Redis временные данные (состояние, код и юзера).
    """
    result = await PasswordRecovery.recover_pass(data.user)
    data_redis = {
        'state': SESSION_STATE_MAIL,
        'code': result['code'],
        'user': data.user
        }
    if result['status_code'] == 200:
        redis_client.set(data.user, json.dumps(data_redis))
        response = JSONResponse(
            content={"message": "Теперь введите код с почты..."},
            status_code=200)
    else:
        response = JSONResponse(content={"message": result["message"]},
                                status_code=result['status_code'])
    return response


@app_auth.post("/recover/reset_code")
async def reset_code(data: CodeConfirm) -> JSONResponse:
    """
    Подтверждение восстановления пароля кодом с почты.

    Args:

        code: Код из из почты.
        login: Логин/почта введённая в предыдущем шаге /recover.

    Returns:

        JSONResponse: Результат подтверждения кода.

        - 200: Успешное подтверждение, возвращает сообщение об успехе.
        - 422: Ошибка валидации, возвращает сообщение об ошибке.
        - 400: Ошибка состояния сессии, почта не указана.
    Notes:

        1. Валидирует данные
        2. По логину/почте введённой в предыдущем шаге /recover,
        достаёт данные из Redis.
        3. Сверяет идентификатор сессии, с идентификатором из Redis.
        4. Сверяет код из почты, с кодом из хранилища Redis.
        5. Сохраняет идентификатор сессии и пользователя, во временное
        хранилище Redis, по логину/почте введённым в шаге /recover.
        6. Очищает старые временные данные в Redis.

        * Сессия очищается через 6 минут, если код неверный. Время изменяется
        в переменных окружения.
    """
    try:
        user_data = redis_client.get(data.login)
        user_data = json.loads(user_data.decode('utf-8'))
        if isinstance(user_data, JSONResponse):
            return user_data
        state = user_data.get('state')
        verification_code = user_data.get('code')
        user = user_data.get('user')
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)

    if state == SESSION_STATE_MAIL:
        if str(verification_code) == str(data.code):
            data_redis = {
                "state": SESSION_STATE_CODE,
                'user': user
                }
            redis_client.set(user, json.dumps(data_redis))
            response = JSONResponse(
                content={"message": "Можете менять пароль!"}, status_code=200)
            redis_client.delete(f"login:{user}")
        else:
            response = JSONResponse(
                content={"message": "Введенный код неверный!"},
                status_code=400)
        return response
    else:
        return JSONResponse(content={"message": "Вы не указали почту!"},
                            status_code=400)


@app_auth.post("/recover/reset_code/change_password")
async def change_password(data: PasswordChange) -> JSONResponse:
    """
    Изменение пароля после восстановления.

    Args:

        "user": Логин/почта введённая в первом шаге /recovery
        "password": Новый пароль.
        "password_two": Подтверждение нового пароля.

    Returns:

        JSONResponse: Результат изменения пароля.
        - 200: Успешное подтверждение, возвращает сообщение об успехе.
        - 422: Ошибка валидации, возвращает сообщение об ошибке.
        - 400: Ошибка состояния сессии, код не введен.

    Notes:

        1. Валидирует данные
        2. По логину/почте введённой в предыдущем шаге /recover,
        достаёт данные из Redis.
        3. Сверяет идентификатор сессии, с идентификатором из Redis.
        4. Меняет пароль в базе данных(сохраняя его в виде хэша).
        5. Удаляет временные данные из Redis.

        * Сессия очищается через 6 минут, если код неверный. Время изменяется
        в переменных окружения.
    """
    try:
        user_data = redis_client.get(data.user)
        user_data = json.loads(user_data.decode('utf-8'))
        if isinstance(user_data, JSONResponse):
            return user_data
        state = user_data.get('state')
        user = user_data.get('user')
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)

    if state == SESSION_STATE_CODE:
        result = await PasswordRecovery.new_password(user, data.password,
                                                     data.password_two)
        if result['status_code'] == 200:
            response = JSONResponse(content={"message": result["message"]},
                                    status_code=result['status_code'])
            redis_client.delete(f"login:{user}")
        else:
            response = JSONResponse(content={"message": result["message"]},
                                    status_code=result['status_code'])
        return response
    else:
        return JSONResponse(content={"message": "Вы не ввели код!"},
                            status_code=400)


@app_logout.post("/")
async def logout(request: Request, data: Token) -> JSONResponse:
    """
    Обработчик выхода пользователя.

    Args:
        request (Request): HTTP запрос.
        data (Token): Токен пользователя для выхода.

    Returns:
        JSONResponse: Результат выхода пользователя.
        - 308: Успешный выход, возможно с перенаправлением.
        - Другие коды: Соответствующие сообщения об ошибках и коды статусов.
    """
    result = await Logout.delete_token(data.token)
    if result['status_code'] == 308:
        # Здесь вы можете указать перенаправление на нужную
        # страницу в другом микросервисе после выхода пользователя
        # <--- код --->
        response = JSONResponse(content={"message": result["message"]},
                                status_code=result['status_code'])
    else:
        response = JSONResponse(content={"message": result["message"]},
                                status_code=result['status_code'])
    return response
