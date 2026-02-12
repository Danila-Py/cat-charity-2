import logging

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.user import get_user_db, get_user_manager
from app.core.config import settings
from app.core.db import get_async_session
from app.models.user import User
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


async def create_superuser(session: AsyncSession) -> None:
    """Создание суперпользователя, если его нет."""
    existing_user = await session.execute(
        select(User).where(User.email == settings.superuser_email)
    )
    if existing_user.scalars().first():
        logger.info(
            "Суперпользователь {settings.superuser_email} уже существует",
        )
        return

    user_data = UserCreate(
        email=settings.superuser_email,
        password=settings.superuser_password,
        is_superuser=True,
        is_active=True,
        is_verified=True,
    )

    async for user_db in get_user_db(session):
        async for user_manager in get_user_manager(user_db):
            await user_manager.create(user_data)
            logger.info(
                "Суперпользователь {settings.superuser_email} успешно создан",
            )
            break
        break


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
    """Lifespan контекст для инициализации при старте."""
    logger.info("Запуск приложения QRKot...")
    async for session in get_async_session():
        await create_superuser(session)
        break
    yield
    logger.info("Завершение приложения QRKot...")