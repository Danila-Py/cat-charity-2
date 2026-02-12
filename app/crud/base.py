from typing import List, Optional, TypeVar

from fastapi.encoders import jsonable_encoder
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation
from app.models.base import BaseCharityDonationModel

ModelType = TypeVar('ModelType', CharityProject, Donation)


class CRUDBase:
    """Базовый класс для получения и создания объекта."""

    def __init__(self, model):
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Optional[CharityProject]:
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession
    ) -> List[CharityProject]:
        db_objs = await session.execute(select(self.model))
        result = db_objs.scalars().all()
        return result

    async def create(
        self,
        obj_in,
        session: AsyncSession,
    ) -> CharityProject:
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(
            self,
            db_obj,
            session: AsyncSession
    ):
        await session.delete(db_obj)
        await session.commit()
        return db_obj


class BaseCharityRepository(CRUDBase):
    """Базовый репозиторий для благотворительных моделей."""

    async def get_active_objects(
        self,
        session: AsyncSession
    ) -> List[BaseCharityDonationModel]:
        conditions = [self.model.fully_invested.is_(False)]
        query = select(self.model).where(
            *conditions
        ).order_by(asc(self.model.create_date))
        result = await session.execute(query)
        return result.scalars().all()
