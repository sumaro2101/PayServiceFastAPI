from typing import Annotated

from fastapi import HTTPException, Path, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.models import Product
from config.database import db_connection
from . import crud
from .common import ErrorCode


async def get_product_by_id(
    product_id: Annotated[int, Path(gt=0)],
    session: AsyncSession = Depends(db_connection.session_geter),
) -> Product:
    product = await crud.get_product(
        session=session,
        product_id=product_id,
        )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorCode.PRODUCT_NOT_FOUND,
            )
    return product
