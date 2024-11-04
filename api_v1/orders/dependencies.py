from typing import Annotated
from sqlalchemy import Select, and_

from fastapi import HTTPException, Path, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.models import Order
from config.models import db_helper
from . import crud


async def get_order_by_id(order_id: Annotated[int,
                                                  Path()],
                            session: AsyncSession = Depends(db_helper.session_geter)) -> Order:
    order = await crud.get_order(session=session,
                                     order_id=order_id)
    if order:
        return order
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail=f'Заказ {order_id} не был найден')


async def get_order_by_user_and_coupone(user_id: int,
                                        coupon_id: int,
                                        session: AsyncSession,
                                        ) -> Order | None:
    stmt = (Select(Order.id)
            .where(and_(Order.user_id == user_id,
                        Order.coupon_id == coupon_id)))
    order = await session.scalar(statement=stmt)
    return order
