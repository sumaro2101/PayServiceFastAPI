from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, relationship

from config.models import Base

if TYPE_CHECKING:
    from .order import Order


class Product(Base):
    """Модель товара
    """
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
    
    orders: Mapped[list['Order']] = relationship(
        secondary='order_product_association',
        back_populates='products',
    )
