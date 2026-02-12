from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseCharityRepository
from app.models.donation import Donation
from app.models.user import User
from app.schemas.donation import DonationCreate


class CRUDDonation(BaseCharityRepository):
    """Класс дополнительных методов модели Donation."""

    async def create_with_user(
        self,
        obj_in: DonationCreate,
        user: User,
        session: AsyncSession,
    ) -> Donation:
        """Создание пожертвования с привязкой к пользователю."""
        obj_in_data = obj_in.dict()
        obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_user_donations(
        self,
        user_id: int,
        session: AsyncSession,
    ) -> List[Donation]:
        """Получение всех пожертвований конкретного пользователя."""
        donations = await session.execute(
            select(Donation)
            .where(Donation.user_id == user_id)
            .order_by(Donation.create_date)
        )
        return donations.scalars().all()


donation_crud = CRUDDonation(Donation)