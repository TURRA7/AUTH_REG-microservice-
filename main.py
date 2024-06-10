import asyncio
import uvicorn

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.api import app_auth, app_reg
from database.FDataBase import create_tables


app = FastAPI()

app.include_router(app_reg)


app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_tables())

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)