import asyncio
import uvicorn

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from api.api import app_auth, app_reg
from config import SECRET_KEY
from database.FDataBase import create_tables, delete_tables


app = FastAPI()

app.include_router(app_reg)
app.include_router(app_auth)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY,
                   max_age=360)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(delete_tables())

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
