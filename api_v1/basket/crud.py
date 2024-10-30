from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from random import getrandbits

from stripe import _error

from config.models import Basket, Product
from loguru import logger
from api_stripe.api import StripeSession, ExpireSession
from api_stripe.handler import error_stripe_handle
from api_v1.auth.utils import int_to_base36
from api_v1.promos.dependencies import get_coupon_by_name
from api_v1.orders.dependencies import get_order_by_user_and_coupone
from .schemas import CouponeNameSchema


async def add_product_basket(basket: Basket,
                             product: Product,
                             session: AsyncSession,
                             ) -> dict:
    try:
        if basket.unique_temporary_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=dict(
                                    basket='В данный момент корзина '
                                    'имеет фиксированное состояние '
                                    'изза ожидающего платежа. '
                                    'Если вы хотите добавить товар, '
                                    'неоходимо отменить платеж.',
                                    ))
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
    coupone = coupone.model_dump(exclude_none=True)
    if coupone:
        name = coupone['number']
        user = basket.user
        coupone_obj = await get_coupon_by_name(
            coupon_name=name,
            session=session,
        )
        promo_in_orders = await get_order_by_user_and_coupone(
            user_id=user.id,
            coupon_id=coupone_obj.id,
            session=session,
        )
        if promo_in_orders:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=dict(coupone='This coupon is already used'))
        coupone = coupone_obj.id
        basket.coupon_id = coupone
    user = basket.user
    products = basket.products
    if not products:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                dict(product='Для покупки нужен минимум один товар')),
                            )
    unique_code = int_to_base36(getrandbits(41))
    stripe = StripeSession(user=user,
                           products=products,
                           unique_code=unique_code,
                           promo=coupone,
                           )
    try:
        stripe_session = await stripe.get_session_payments()
    except _error.InvalidRequestError as ex:
        message = error_stripe_handle(ex)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=dict(payment=message))
    if basket.session_id:
        await ExpireSession(session_id=basket.session_id).expire_session()
    basket.unique_temporary_id = unique_code
    basket.session_id = stripe_session.id
    await session.commit()
    return stripe_session


async def delete_product_basket(basket: Basket,
                                product: Product,
                                session: AsyncSession,
                                ) -> dict:
    try:
        if basket.unique_temporary_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=dict(
                                    basket='В данный момент корзина '
                                    'имеет фиксированное состояние '
                                    'изза ожидающего платежа. '
                                    'Если вы хотите добавить товар, '
                                    'неоходимо отменить платеж.',
                                    ))
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
    if basket.unique_temporary_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=dict(
                                    basket='В данный момент корзина '
                                    'имеет фиксированное состояние '
                                    'изза ожидающего платежа. '
                                    'Если вы хотите добавить товар, '
                                    'неоходимо отменить платеж.',
                                    ))
    basket.products.clear()
    await session.commit()
    return dict(state='success',
                detail='Basket is clear',
                )
