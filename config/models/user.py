from datetime import datetime
from typing import Union, TYPE_CHECKING

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, func

from config.models import Base

if TYPE_CHECKING:
    from .post import Post
    from .profile import Profile


class User(Base):
    """Модель пользователя
    """
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[str] = mapped_column(nullable=True)
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    password1: Mapped[str]
    password2: Mapped[str]

    posts: Mapped[list['Post']] = relationship(back_populates='user')
    profile: Mapped['Profile'] = relationship(back_populates='user')
