from sqlalchemy.orm import Mapped, relationship, mapped_column

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
    unique_temporary_id: Mapped[str | None] = mapped_column(nullable=True,
                                                     default=None,
                                                     )

    products: Mapped[list['Product']] = relationship(
        secondary='basket_product_association',
        back_populates='baskets',
    )
