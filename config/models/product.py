from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import func

from functools import partial

from datetime import datetime

from config.models import Base

if TYPE_CHECKING:
    from .order import Order


ADD_NOW_TIME = partial(mapped_column,
                       insert_default=func.now(),
                       server_default=func.now(),
                       )


class Product(Base):
    """Модель товара
    """
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
    created_at: Mapped[datetime] = ADD_NOW_TIME()
    updated_at: Mapped[datetime] = ADD_NOW_TIME()
    is_active: Mapped[bool] = mapped_column(default=True)

    orders: Mapped[list['Order']] = relationship(
        secondary='order_product_association',
        back_populates='products',
    )
