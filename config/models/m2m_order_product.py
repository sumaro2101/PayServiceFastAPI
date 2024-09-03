from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint

from .base import Base

order_product_association_table = Table(
    'oreder_product_association',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('order_id', ForeignKey('orders.id'), nullable=False),
    Column('product_id', ForeignKey('products.id'), nullable=False),
    UniqueConstraint('order_id', 'product_id', name='idx_unique_order_product'),
)