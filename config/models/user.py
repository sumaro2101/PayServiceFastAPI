from datetime import datetime
from typing import Union

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, func

from config.models import Base


class User(Base):
    """Модель пользователя
    """
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[str] = mapped_column(nullable=True)
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    password1: Mapped[str]
    password1: Mapped[str]
