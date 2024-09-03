from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, relationship

from config.models import Base
from .m2m_order_product import order_product_association_table as m2m_order_product

if TYPE_CHECKING:
    from .order import Order


class Product(Base):
    """Модель товара
    """
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
    
    orders: Mapped[list['Order']] = relationship(
        secondary=m2m_order_product,
        back_populates='products',
    )
