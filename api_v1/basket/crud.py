from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from config.models import Basket, Product


async def add_product_basket(basket: Basket,
                             product: Product,
                             session: AsyncSession,
                             ) -> dict:
    try:
        basket.products.append(product)
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=dict(product='Этот товар уже был добален в корзину'))
    return dict(state='success',
                detail='Product is add success',
                product=product,
                )

async def delete_product_basket(basket: Basket,
                                product: Product,
                                session: AsyncSession,
                                ) -> dict:
    try:
        basket.products.remove(product)
        await session.commit()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=dict(product='Этого товара нет в корзине'))
    return dict(state='success',
                detail='Product is delete',
                product=product.name,
                )

async def delete_all_products(basket: Basket,
                              session: AsyncSession,
                              ) -> dict:
    basket.products.clear()
    await session.commit()
    return dict(state='success',
                detail='Basket is clear',
                )
