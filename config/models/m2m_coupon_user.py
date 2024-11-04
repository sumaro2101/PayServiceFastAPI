from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class CouponUserAssociation(Base):
    __tablename__ = 'coupon_user_association'
    __table_args__ = (
        UniqueConstraint('coupon_id', 'user_id', name='idx_unique_coupon_user'),
    )

    coupon_id: Mapped[int] = mapped_column(ForeignKey('coupons.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
