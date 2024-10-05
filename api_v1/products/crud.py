from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exc
from sqlalchemy.engine import Result

from config.models.product import Product
from .schemas import ProductCreate, ProductUpdate
from api_stripe.api import Stripe


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
    stmt = select(Product).where(Product.id==product_id)
    result: Result = await session.execute(stmt)
    product = result.scalars().first()
    return product


async def product_create(session: AsyncSession,
                         product: ProductCreate) -> Product:
    """ Создание продукта
    """
    product = Product(**product.model_dump())
    session.add(product)
    await session.commit()
    session.refresh(product)
    stripe = Stripe(product)
    await stripe.register()
    return product


async def product_update(session: AsyncSession,
                         product: Product,
                         product_update: ProductUpdate) -> Product:
    """Обновление продукта
    """
    
    for name, value in product_update.model_dump(exclude_unset=True).items():
        setattr(product, name, value)
    await session.commit()
    return product


async def product_delete(session: AsyncSession,
                         product: Product,
                         ) -> None:
    """Удаление продукта
    """
    await session.delete(product)
    await session.commit()
