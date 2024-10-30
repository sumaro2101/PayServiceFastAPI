from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import ForeignKey

from typing import TYPE_CHECKING

from config.models.base import Base
from config.models.mixins import UserRelationMixin
from .utils import NULL_FIELD_INSTANCE

if TYPE_CHECKING:
    from config.models import Product
    from config.models import Coupon


class Basket(UserRelationMixin, Base):
    """
    Корзина покупок пользователя
    """
    _user_id_unique = True
    _user_back_populates = 'basket'
    unique_temporary_id: Mapped[str | None] = NULL_FIELD_INSTANCE()
    session_id: Mapped[str | None] = NULL_FIELD_INSTANCE()
    coupon_id: Mapped[int | None] = NULL_FIELD_INSTANCE(ForeignKey('coupons.id'))

    products: Mapped[list['Product']] = relationship(
        secondary='basket_product_association',
        back_populates='baskets',
    )
    coupon: Mapped['Coupon'] = relationship(
        back_populates='baskets',
    )
