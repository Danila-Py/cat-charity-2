from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import CommonMixin
from app.models.base import BaseCharityDonationModel


class CharityProject(CommonMixin, BaseCharityDonationModel):
    """Модель благотворительного проекта."""

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return self.name