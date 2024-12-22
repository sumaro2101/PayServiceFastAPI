from typing import Annotated

from fastapi import HTTPException, Path, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.models import Order
from config.database import db_connection
from . import crud


async def get_order_by_id(
    order_id: Annotated[int, Path(gt=0)],
    session: AsyncSession = Depends(db_connection.session_geter),
) -> Order:
    order = await crud.get_order(
        session=session,
        order_id=order_id,
        )
    if order:
        return order
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Заказ {order_id} не был найден',
        )
