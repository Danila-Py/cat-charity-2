from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_charity_project_before_edit,
                                check_charity_project_exists,
                                check_charity_project_is_not_invested,
                                check_name_duplicate)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud import charity_project_crud
from app.crud.donation import donation_crud
from app.models.user import User
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.investing import distribute_funds

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    summary='Создание нового благотворительного проекта',
    description='Создать целевой проект.'
)
async def create_new_charityproject(
    charityproject: CharityProjectCreate,
    session: SessionDep,
    user: User = Depends(current_superuser),
):
    """Добавление благотворительного проекта."""
    await check_name_duplicate(charityproject.name, session)
    new_project = await charity_project_crud.create(charityproject, session)
    return await distribute_funds(new_project, donation_crud, session)


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
    summary='Получение списка всех благотворительных проектов',
    description='Доступно всем пользователям (включая анонимных).'
)
async def get_all_charityproject(
    session: SessionDep
):
    """Получение всех благотворительных проектов."""
    return await charity_project_crud.get_multi(session)


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    summary='Обновление благотворительного проекта',
    description=(
        'Редактировать целевой проект. '
        'Закрытый проект нельзя редактировать; нельзя установить требуемую '
        'сумму меньше уже вложенной.'
    )
)
async def partially_update_charityproject(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: SessionDep,
    user: User = Depends(current_superuser),
):
    """Обновление благотворительного проекта."""
    project = await check_charity_project_exists(
        project_id, session
    )
    await check_charity_project_before_edit(project, obj_in)
    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)

    updated_project = await charity_project_crud.update(
        project, obj_in, session
    )
    if not updated_project.fully_invested:
        updated_project = await distribute_funds(
            updated_project,
            donation_crud,
            session
        )
    return updated_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    summary='Удаление благотворительного проекта',
    description='Только для суперпользователей.'
    ' Нельзя удалить проект, в который были внесены средства.'
)
async def delete_charityproject(
    project_id: int,
    session: SessionDep,
    user: User = Depends(current_superuser),
):
    """Удаление благотворительного проекта."""
    charity_project = await check_charity_project_exists(
        project_id, session)
    await check_charity_project_is_not_invested(charity_project)
    return await charity_project_crud.delete(charity_project, session)