from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result

from loguru import logger

from fastapi import HTTPException, status

from config.models.product import Product
from .schemas import ProductCreate, ProductUpdate
from .utils import add_params
from api_stripe.abs import Stripe


async def get_products(session: AsyncSession) -> Union[list[Product] |
                                                       None]:
    """ Получение всех товаров
    """
    stmt = select(Product).order_by(Product.id)
    result: Result = await session.execute(stmt)
    products = result.scalars().all()
    return list(products)


async def get_product(session: AsyncSession,
                      product_id: int) -> Union[Product | None]:
    """ Получение товара по ID
    """
    stmt = select(Product).where(Product.id == product_id)
    product = await session.scalar(stmt)
    return product


async def product_create(session: AsyncSession,
                         product: ProductCreate,
                         stripe_action: Stripe,
                         ) -> Product:
    """ Создание продукта
    """
    prefetch_create = Product(**product.model_dump())
    session.add(prefetch_create)
    await session.commit()
    await session.refresh(prefetch_create)
    stripe = stripe_action(prefetch_create.__dict__)
    await stripe.action()
    return prefetch_create


async def product_update(session: AsyncSession,
                         product: Product,
                         product_update: ProductUpdate,
                         stripe_action: Stripe,
                         ) -> Product:
    """Обновление продукта
    """
    updated_params = product_update.model_dump(exclude_unset=True)
    if product_update.price == product.price:
        product_update.price = None
    for name, value in updated_params.items():
        setattr(product, name, value)
    await session.commit()
    logger.info(f'update_params = {product_update.model_dump(exclude_none=True)}')
    if product_update.model_dump(exclude_none=True):
        stripe_update = add_params(updated_params,
                                   id=product.id,
                                   )
        stripe = stripe_action(stripe_update)
        await stripe.action()
    return product


async def product_activate(session: AsyncSession,
                           product: Product,
                           stripe_action: Stripe
                           ) -> None:
    """Удаление продукта
    """
    if product.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=dict(product='This product is already active'),
                            )
    product.is_active = True
    await session.commit()
    stripe = stripe_action(target=dict(id=product.id))
    await stripe.action()
    return product


async def product_deactivate(session: AsyncSession,
                             product: Product,
                             stripe_action: Stripe
                             ) -> None:
    """Удаление продукта
    """
    if not product.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=dict(product='This product is already non active'),
                            )
    product.is_active = False
    await session.commit()
    stripe = stripe_action(target=dict(id=product.id))
    await stripe.action()
    return product
