from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class BasketProductAssociation(Base):
    __tablename__ = 'basket_product_association'
    __table_args__ = (
        UniqueConstraint('basket_id', 'product_id', name='idx_unique_basket_product'),
    )

    basket_id: Mapped[int] = mapped_column(ForeignKey('baskets.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    count: Mapped[int] = mapped_column(default=1, server_default='1')
