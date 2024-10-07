from sqlalchemy.orm import Mapped, relationship

from typing import TYPE_CHECKING

from config.models.base import Base
from config.models.mixins import UserRelationMixin

if TYPE_CHECKING:
    from config.models import Product


class Basket(UserRelationMixin, Base):
    """
    Корзина покупок пользователя
    """
    _user_id_unique = True
    _user_back_populates = 'basket'
    
    products: Mapped[list['Product']] = relationship(
        secondary='basket_product_association',
        back_populates='baskets',
    )
