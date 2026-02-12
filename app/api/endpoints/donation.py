from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud import donation_crud
from app.crud.charity_project import charity_project_crud
from app.models.user import User
from app.schemas.donation import DonationCreate, DonationDB, DonationFullInfoDB
from app.services.investing import distribute_funds

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get(
    '/',
    response_model=list[DonationFullInfoDB],
    response_model_exclude_none=True,
    summary='Все пожертвования',
    description='Получение списка всех пожертвований (для суперпользователей).'
)
async def get_all_donations(
        session: SessionDep,
        user: User = Depends(current_superuser),
):
    return await donation_crud.get_multi(session=session)


@router.get(
    '/my',
    response_model=list[DonationDB],
    response_model_exclude_none=True,
    summary='Мои пожертвования',
    description='Получение списка своих пожертвований.'
)
async def get_my_donations(
    session: SessionDep,
    user: User = Depends(current_user),
):
    return await donation_crud.get_user_donations(user.id, session)


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
    summary='Создать пожертвование',
    description='Создание нового пожертвования'
)
async def create_new_donation(
    donation: DonationCreate,
    session: SessionDep,
    user: User = Depends(current_user),
):
    new_donation = await donation_crud.create_with_user(
        donation,
        user,
        session
    )
    return await distribute_funds(
        new_donation,
        charity_project_crud,
        session
    )