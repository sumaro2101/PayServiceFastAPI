from typing import Annotated

from fastapi import HTTPException, Path, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.models.product import Product
from config.models import db_helper
from . import crud


async def get_product_by_id(product_id: Annotated[int,
                                                  Path()],
                            session: AsyncSession = Depends(db_helper.session_geter)) -> Product:
    product = await crud.get_product(session=session,product_id=product_id)
    if product:
        return product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail=f'Продукт {product_id} не был найден')
