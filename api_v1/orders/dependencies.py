from typing import Annotated

from fastapi import Path, Depends
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
    return order
