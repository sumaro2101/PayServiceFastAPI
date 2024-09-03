from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Union, TYPE_CHECKING

from .base import Base
from .mixins import UserRelationMixin
from .m2m_order_product import order_product_association_table as m2m_order_product

if TYPE_CHECKING:
    from .product import Product


class Order(Base):
    """Модель заказа
    """

    promocode: Mapped[Union[str, None]] = mapped_column(nullable=True)
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now(),
                                                  server_default=func.now(),
                                                  )
    products: Mapped[list['Product']] = relationship(
        secondary=m2m_order_product,
        back_populates='orders',
    )
