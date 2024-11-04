from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class OrderProductAssociation(Base):
    __tablename__ = 'order_product_association'
    __table_args__ = (
        UniqueConstraint('order_id', 'product_id', name='idx_unique_order_product'),
    )

    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    count: Mapped[int] = mapped_column(default=1, server_default='1')
