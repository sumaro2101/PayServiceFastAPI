from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from typing import TYPE_CHECKING

from config.models import Base
from .utils import ADD_NOW_TIME, EMPTY_TEXT_DEFAULT

if TYPE_CHECKING:
    from config.models import User
    from .order import Order
    from config.models import Basket


class Coupon(Base):
    """
    Модель скидочного купона
    """    
    number: Mapped[str] = mapped_column(unique=True)
    discount: Mapped[float]
    description: Mapped[str] = EMPTY_TEXT_DEFAULT()
    create_at: Mapped[datetime] = ADD_NOW_TIME()
    end_at: Mapped[datetime]
    active: Mapped[bool] = mapped_column(default=True)

    users: Mapped[list['User']] = relationship(
        back_populates='coupons',
        secondary='coupon_user_association',
        )
    orders: Mapped[list['Order']] = relationship(
        back_populates='coupon',
    )
    baskets: Mapped[list['Basket']] = relationship(
        back_populates='coupon',
    )
