from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from .base import Base
from .mixins import UserRelationMixin
from .utils import ADD_NOW_TIME

if TYPE_CHECKING:
    from .product import Product
    from .promo import Coupon


class Order(UserRelationMixin, Base):
    """Модель заказа
    """
    _user_back_populates = 'orders'

    coupon_id: Mapped[int | None] = mapped_column(ForeignKey('coupons.id'),
                                                  nullable=True,
                                                  default=None,
                                                  )
    create_date: Mapped[datetime] = ADD_NOW_TIME()
    coupon: Mapped['Coupon'] = relationship(
        back_populates='orders',
    )
    products: Mapped[list['Product']] = relationship(
        secondary='order_product_association',
        back_populates='orders',
    )
