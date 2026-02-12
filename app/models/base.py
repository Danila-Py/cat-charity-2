from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class BaseCharityDonationModel(Base):
    """Базовая модель для проекта и пожертвований."""

    __abstract__ = True

    full_amount: Mapped[int] = mapped_column(
        Integer, CheckConstraint(
            'full_amount >= 0',
            name='check_full_amount_positive'
        ), nullable=False
    )
    invested_amount: Mapped[int] = mapped_column(
        Integer, CheckConstraint(
            'invested_amount >= 0',
            name='check_invested_amount_non_negative'
        ), CheckConstraint(
            'invested_amount <= full_amount',
            name='check_invested_le_full'
        ),
        default=0
    )
    fully_invested: Mapped[bool] = mapped_column(
        Boolean, default=False
    )
    create_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    close_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=True
    )
