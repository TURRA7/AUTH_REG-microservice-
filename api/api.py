from typing import Annotated
from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from database.FDataBase import User, select_user, add_user
from models.models import UserModel

templates = Jinja2Templates(directory="templates")


app_reg = APIRouter()
app_auth = APIRouter()

@app_reg.get("/registration", response_class=HTMLResponse)
async def template_reg(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("reg/reg.html", {"request": request})


@app_reg.post("/registration")
async def registration(request: Request,
                       login: Annotated[str, Form()],
                       password: Annotated[str, Form()],
                       password_two: Annotated[str, Form()]
                       ) -> JSONResponse:
    user = await select_user(login)
    if user:
        return JSONResponse(content={"message": "Пользователь с таким логином, уже существует!"}, status_code=400)
    await add_user(login, password)
    return JSONResponse(content={"message": "Регистрация успешна!"}, status_code=200)


@app_reg.get("/authorization", response_class=HTMLResponse)
async def registration(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("auth/auth.html", {"request": request})


@app_reg.post("/authorization")
async def authorization(request: Request,
                        login: Annotated[str, Form()],
                        password: Annotated[str, Form()]
                        ) -> JSONResponse:
    user = await select_user(login)
    if not user or user[0].password != password:
        return JSONResponse(content={"message": "Неверный логин или пароль!"}, status_code=400)
    else:
        return JSONResponse(content={"message": "Авторизация успешна!"}, status_code=200)
    