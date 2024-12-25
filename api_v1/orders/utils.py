from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, or_
from fastapi import HTTPException, status

from config.models import Product
from .common import ErrorCode


async def get_list_orders_to_append(session: AsyncSession,
                                    ids_product: list[int]):
    if not ids_product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=ErrorCode.CANT_BE_EMPTY_LIST_PRODUCTS,
                            )
    stmt = Select(Product).where(or_(Product.id == id for id in ids_product))
    products = await session.scalars(stmt)
    list_products = list(products)
    if ids := have_products_not_exists(
        ids_product,
        list_products,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={'code': ErrorCode.NOT_FOUND_PRODUCTS,
                    'reason': f'Not found products ids {ids}',
                    }
        )
    return list_products


def have_products_not_exists(
    product_ids: list[int],
    product_exit: list[Product],
) -> set[int]:
    ids_exit = {product.id for product in product_exit}
    return set(product_ids) - ids_exit
