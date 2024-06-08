"""Database module based on SQLAlchemy."""

import os

from config import PG_USER, PG_PASS, PG_HOST, PG_PORT, PG_DB

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


engine = create_async_engine(
    f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}",
    echo=True)


new_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    """Table for user registration and authorization."""
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, password={self.password!r})"
    

async def create_tables():
    """Asynchronous function for adding specified tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables():
    """Asynchronous function to delete all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
