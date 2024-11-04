from typing import Optional

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Text

from config.models import Base
from .mixins import UserRelationMixin
from .utils import EMPTY_TEXT_DEFAULT


class Profile(UserRelationMixin, Base):
    """Модель пользователя
    """
    _user_id_unique = True
    _user_back_populates = 'profile'
    
    first_name: Mapped[Optional[str]] = mapped_column(String(40))
    last_name: Mapped[Optional[str]] = mapped_column(String(60))
    bio: Mapped[Optional[str]] = EMPTY_TEXT_DEFAULT()
