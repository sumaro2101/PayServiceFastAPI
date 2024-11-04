from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import UserRelationMixin
from .utils import EMPTY_TEXT_DEFAULT


class Post(UserRelationMixin, Base):
    """Модель поста
    """
    _user_back_populates = 'posts'

    title: Mapped[str] = mapped_column(String(100))
    body: Mapped[str] = EMPTY_TEXT_DEFAULT()
