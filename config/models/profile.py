from typing import Optional

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Text

from config.models import Base
from .mixins import UserRelationMixin


class Profile(UserRelationMixin, Base):
    """Модель пользователя
    """
    _user_id_unique = True
    _user_back_populates = 'profile'
    
    first_name: Mapped[Optional[str]] = mapped_column(String(40))
    last_name: Mapped[Optional[str]] = mapped_column(String(60))
    bio: Mapped[Optional[str]] = mapped_column(Text)
