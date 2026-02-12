from datetime import datetime
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseCharityRepository
from app.models.base import BaseCharityDonationModel

T = TypeVar('T', bound=BaseCharityDonationModel)


async def distribute_funds(
    source: T,
    repository: BaseCharityRepository,
    session: AsyncSession,
) -> T:
    """Распределяет средства от source к противоположному типу объектов."""
    targets = await repository.get_active_objects(session)

    if targets:
        available_amount = source.full_amount - source.invested_amount

        for target in targets:
            if available_amount <= 0:
                break

            needed_amount = target.full_amount - target.invested_amount
            to_transfer = min(needed_amount, available_amount)

            if to_transfer <= 0:
                continue
            target.invested_amount += to_transfer
            if target.invested_amount >= target.full_amount:
                target.fully_invested = True
                target.close_date = datetime.now()
            source.invested_amount += to_transfer
            available_amount -= to_transfer

    if source.invested_amount >= source.full_amount:
        source.fully_invested = True
        source.close_date = datetime.now()

    session.add(source)
    await session.commit()
    await session.refresh(source)
    return source