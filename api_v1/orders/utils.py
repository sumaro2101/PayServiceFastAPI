from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, or_

from fastapi import HTTPException, status

from config.models import Product


async def get_list_orders_to_append(session: AsyncSession,
                                    ids_product: list[int]):
    if not ids_product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Неоходимо указать список продуктов')
    stmt = Select(Product).where(or_(Product.id == id for id in ids_product))
    products = await session.scalars(stmt)
    return list(products)
