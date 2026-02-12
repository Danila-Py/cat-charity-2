from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import CommonMixin
from app.models.base import BaseCharityDonationModel


class Donation(CommonMixin, BaseCharityDonationModel):
    """Модель пожертвований."""

    comment: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'),
        nullable=False
    )