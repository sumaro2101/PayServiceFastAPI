from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status

from config.models.product import Product
from .schemas import ProductCreate, ProductUpdate
from .utils import add_params
from .dao import ProductDAO
from .common import ErrorCode
from api_v1.products.tasks import (
    create_stripe_item_task,
    update_stripe_item_task,
    activate_stripe_item_task,
    deactivate_stripe_item_task,
    )


async def get_products(session: AsyncSession) -> Union[list[Product] |
                                                       None]:
    """
    Получение всех товаров
    """
    return await ProductDAO.find_all_items_by_args(
        session=session,
        order_by=(Product.id,),
    )


async def get_product(session: AsyncSession,
                      product_id: int) -> Union[Product | None]:
    """
    Получение товара по ID
    """
    return await ProductDAO.find_item_by_args(
        session=session,
        id=product_id,
    )


async def product_create(session: AsyncSession,
                         product: ProductCreate,
                         ) -> Product:
    """
    Создание продукта
    """
    product = await ProductDAO.add(
        session=session,
        **product.model_dump()
    )
    values = dict(id=product.id,
                  name=product.name,
                  price=product.price)
    create_stripe_item_task.delay(values)
    return product


async def product_update(session: AsyncSession,
                         product: Product,
                         product_update: ProductUpdate,
                         ) -> Product:
    """
    Обновление продукта
    """
    updated_params = product_update.model_dump(exclude_unset=True)
    if product_update.price == product.price:
        product_update.price = None
    await ProductDAO.update(
        session=session,
        instance=product,
        **updated_params,
    )
    if product_update.model_dump(exclude_none=True):
        stripe_update = add_params(updated_params,
                                   id=product.id,
                                   )
        update_stripe_item_task.delay(stripe_update)
    return product


async def product_activate(session: AsyncSession,
                           product: Product,
                           ) -> None:
    """
    Активация продукта
    """
    if product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.PRODUCT_ALREADY_ACTIVE,
            )
    product.is_active = True
    await session.commit()
    activate_stripe_item_task.delay(dict(id=product.id))
    return product


async def product_deactivate(session: AsyncSession,
                             product: Product,
                             ) -> None:
    """
    Деактивация продукта
    """
    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=dict(product='This product is already non active'),
            )
    product.is_active = False
    await session.commit()
    deactivate_stripe_item_task.delay(dict(id=product.id))
    return product
