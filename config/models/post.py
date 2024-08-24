from typing import TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Post(Base):
    """Модель поста
    """
    title: Mapped[str] = mapped_column(String(100))
    body: Mapped[str] = mapped_column(
        Text,
        default='',
        server_default='',
    )
    
    post_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
    )
    user: Mapped['User'] = relationship(
        back_populates='posts'
    )
