"""Database module based on SQLAlchemy."""

from typing import List

from config import PG_USER, PG_PASS, PG_HOST, PG_PORT, PG_DB

from sqlalchemy import String, select, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession)
from sqlalchemy.orm import sessionmaker


engine = create_async_engine(
    f"postgresql+asyncpg://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}",
    echo=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

class Base(DeclarativeBase):
    pass


class User(Base):
    """Table for user registration and authorization."""
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    role_id: Mapped[int] = mapped_column(default=1)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, password={self.password!r})"
    

async def create_tables() -> None:
    """Asynchronous function for adding specified tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables() -> None:
    """Asynchronous function to delete all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    

async def select_by_user(login) -> List[User]:
    """Getting a specific user from a table, by login."""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.name == login))
        users = result.scalars().all()
        return users
    

async def select_by_email(email) -> List[User]:
    """Getting a specific user from a table, by email."""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.email == email))
        users = result.scalars().all()
        return users
        

async def add_user(email, login, password) -> None:
    """Adding a user to a table."""
    async with AsyncSession(engine) as session:
        async with session.begin():
            result = User(email=email, name=login, password=password)
            session.add(result)
            await session.commit()
