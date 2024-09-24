"""Database module based on SQLAlchemy."""

import re
from typing import List

from config import PG_USER, PG_PASS, PG_HOST, PG_PORT, PG_DB

from sqlalchemy import String, select, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession)
from sqlalchemy.orm import sessionmaker


async def is_valid_email(email) -> bool:
    """
    Проверяет, является ли строка допустимым email адресом.

    Args:

        email (str): Строка для проверки.

    Returns:

        bool: True, если строка соответствует формату email, иначе False.
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_regex, email):
        return True
    else:
        return False


engine = create_async_engine(
    f"postgresql+asyncpg://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}",
    echo=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


class User(Base):
    """Таблица пользователя для регистрации и аутентификации."""
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    role_id: Mapped[int] = mapped_column(default=1)
    is_verified: Mapped[int] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"


async def create_tables() -> None:
    """Функция создания таблиц."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables() -> None:
    """Функция удаления таблиц."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def select_by_user(login) -> List[User]:
    """
    Получение данных из таблцы по логину.

    args:

        login: логин пользователя.
    """
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.name == login))
        user = result.scalars().first()
        return user


async def select_by_email(email) -> List[User]:
    """
    Получение данных из таблцы по почте.

    args:

        email: почта пользователя.
    """
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        return user


async def add_user(email, login, password) -> None:
    """
    Добавление пользователя в таблицу.

    args:

        email: почта пользователя.
        login: логин пользователя.
        password: пароль пользователя.
    """
    async with AsyncSession(engine) as session:
        async with session.begin():
            result = User(email=email, name=login, password=password)
            session.add(result)
            await session.commit()


async def update_password(email, password) -> None:
    """
    Изменение пароля пользователя по указанной почте.

    args:

        email: почта пользователя.
        password: пароль пользователя.
    """
    async with AsyncSession(engine) as session:
        async with session.begin():
            user = await session.execute(
                select(User).where(User.email == email))
            result = user.scalars().first()
            if result:
                result.password = password
                await session.commit()
            else:
                return {"message": f"User with login {email} not found."}


async def update_is_active(login: str, is_verified: bool):
    """
    Изменение активности пользователя.

    args:

        user: логин/почта юзера
        bool: актуальное состояние пользователя.
    """
    async with AsyncSession(engine) as session:
        async with session.begin():
            if await is_valid_email(login):
                user = await session.execute(
                    select(User).where(User.email == login))
            else:
                user = await session.execute(
                    select(User).where(User.name == login))
            result = user.scalars().first()
            if result:
                result.is_verified = is_verified
                await session.commit()
            else:
                return {"message": f"User with login {user} not found."}
