from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from random import getrandbits

from config.models import Basket, Product
from loguru import logger
from api_stripe.api import StripeSession
from api_v1.auth.utils import int_to_base36
from api_v1.promos.dependencies import get_coupon_by_name
from .schemas import CouponeNameSchema


async def add_product_basket(basket: Basket,
                             product: Product,
                             session: AsyncSession,
                             ) -> dict:
    try:
        if not product.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=dict(product='This product is not active'),
                                )
        basket.products.append(product)
        logger.info(basket.products)
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=dict(product='Этот товар уже был добален в корзину'))
    return dict(state='success',
                detail='Product is add success',
                product=product,
                )


async def buy_products(coupone: CouponeNameSchema | None,
                       basket: Basket,
                       session: AsyncSession,
                       ):
    if coupone:
        coupone_obj = await get_coupon_by_name(
            coupon_name=coupone.number,
            session=session,
        )
        coupone = coupone_obj.id
    user = basket.user
    products = basket.products
    if not products:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                dict(product='Для покупки нужен минимум один товар')),
                            )
    unique_code = int_to_base36(getrandbits(41))
    logger.info(f'unique_code = {unique_code}')
    basket.unique_temporary_id = unique_code
    await session.commit()
    logger.info(f'unique code before = {basket.unique_temporary_id}')
    stripe = StripeSession(user=user,
                           products=products,
                           unique_code=unique_code,
                           promo=coupone,
                           )
    session = await stripe.get_session_payments()
    return session


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
