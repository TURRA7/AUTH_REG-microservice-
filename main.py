import asyncio
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from api.api import app_auth, app_reg, app_logout
from config import SECRET_KEY
from database.FDataBase import create_tables, delete_tables
from redis_tools.redis_tools import lifespan


app = FastAPI(lifespan=lifespan)

app.include_router(app_reg)
app.include_router(app_auth)
app.include_router(app_logout)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY,
                   max_age=360)
app.add_middleware(SentryAsgiMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def main():
    await create_tables()

if __name__ == "__main__":
    asyncio.run(main())

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
