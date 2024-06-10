from typing import Annotated
from werkzeug.security import generate_password_hash, check_password_hash

from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from database.FDataBase import User, select_by_user, select_by_email, add_user
from models.models import UserModel

templates = Jinja2Templates(directory="templates")


app_reg = APIRouter()
app_auth = APIRouter()


@app_reg.get("/registration", response_class=HTMLResponse)
async def template_reg(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("reg/reg.html", {"request": request})


@app_reg.post("/registration")
async def registration(request: Request,
                       email: Annotated[str, Form()],
                       login: Annotated[str, Form()],
                       password: Annotated[str, Form()],
                       password_two: Annotated[str, Form()]
                       ) -> JSONResponse:
    user = await select_by_user(login)
    if user:
        return JSONResponse(content={"message": "Пользователь с таким логином, уже существует!"}, status_code=400)
    await add_user(email, login, generate_password_hash(password))
    return JSONResponse(content={"message": "Регистрация успешна!"}, status_code=200)


@app_auth.get("/authorization", response_class=HTMLResponse)
async def template_auth(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("auth/auth.html", {"request": request})


@app_auth.post("/authorization")
async def authorization(request: Request,
                        login: Annotated[str, Form()],
                        password: Annotated[str, Form()]
                        ) -> JSONResponse:
    if "@" in login:
        user = await select_by_email(login)
    else:
        user = await select_by_user(login)
    if not user or not check_password_hash(user[0].password, password):
        return JSONResponse(content={"message": "Неверный логин или пароль!"}, status_code=400)
    else:
        return JSONResponse(content={"message": "Авторизация успешна!"}, status_code=200)
    