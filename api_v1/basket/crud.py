from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from random import getrandbits

from stripe import _error

from config.models import Basket, Product
from loguru import logger
from api_stripe.api import StripeSession, ExpireSession
from api_stripe.types import Session
from api_stripe.handler import error_stripe_handle
from api_v1.auth.utils import int_to_base36
from api_v1.promos.dependencies import get_coupon_by_name
from api_v1.orders.dependencies import get_order_by_user_and_coupone
from config.models.promo import Coupon
from config.models.user import User
from config.config import settings
from .schemas import CouponeNameSchema


class Payment:
    """
    Класс отвечающий за корректную логику
    получения платежей
    """

    _RANDBITS = settings.RANDBITS

    def __init__(self,
                 coupon: CouponeNameSchema,
                 user: User,
                 basket: Basket,
                 session: AsyncSession,
                 ) -> None:
        self.coupon = coupon.number
        self.basket = basket
        self.products = basket.products
        self.user = user
        self._session = session
        self._unique_code = None

    async def _get_coupon(self,
                          coupon_name: str,
                          session: AsyncSession,
                          ) -> Coupon:
        coupon = await get_coupon_by_name(
            coupon_name=coupon_name,
            session=session,
        )
        return coupon

    @classmethod
    async def check_coupon_usage(cls,
                                 coupon_id: int,
                                 user_id: int,
                                 session: AsyncSession,
                                 ) -> None:
        promo_in_orders = await get_order_by_user_and_coupone(
            user_id=user_id,
            coupon_id=coupon_id,
            session=session,
        )
        if promo_in_orders:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=dict(coupone='This coupon '
                                            'is already used'))
        return

    def _check_coupon_having(self,
                             user: User,
                             coupon: Coupon,
                             ) -> None:
        if coupon not in user.coupons:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=dict(coupon='You not have this coupon'))

    @classmethod
    def check_products(cls,
                       products: list[Product],
                       ) -> None:
        if not products:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=(
                                    dict(product='Для покупки нужен '
                                         'минимум один товар')),
                                )

    @classmethod
    async def exripe_session(cls,
                             session_id: str,
                             ) -> None:
        if session_id:
            await ExpireSession(session_id=session_id).expire_session()
        return

    def _generate_unique_code(self) -> str:
        unique_code = int_to_base36(getrandbits(self._RANDBITS))
        self._unique_code = unique_code
        return self._unique_code

    @classmethod
    async def render_session(cls,
                             session: StripeSession,
                             ) -> Session:
        try:
            stripe_session = await session.get_session_payments()
        except _error.InvalidRequestError as ex:
            message = error_stripe_handle(ex)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=dict(payment=message))
        return stripe_session

    async def _set_basket_instanse(self,
                                   basket: Basket,
                                   unique_code: str,
                                   session_id: str,
                                   session: AsyncSession,
                                   ) -> Basket:
        basket.unique_temporary_id = unique_code
        basket.session_id = session_id
        await session.commit()
        return basket

    async def _get_session(self,
                           user: User,
                           coupon: str,
                           basket: Basket,
                           products: list[Product],
                           session: AsyncSession,
                           ) -> Session:
        if coupon:
            coupon = await self._get_coupon(
                coupon_name=coupon,
                session=session,
            )
            self._check_coupon_having(
                user=user,
                coupon=coupon
            )
            coupon = coupon.id
            await self.check_coupon_usage(
                coupon_id=coupon,
                user_id=user.id,
                session=session,
            )
        self.check_products(products=products)
        unique_code = self._generate_unique_code()
        stripe = StripeSession(user=user,
                               products=products,
                               unique_code=unique_code,
                               promo=coupon,
                               )
        payment_session = await self.render_session(
            session=stripe,
        )
        session_id = payment_session.id
        await self.exripe_session(
            session_id=session_id,
        )
        await self._set_basket_instanse(
            basket=basket,
            unique_code=unique_code,
            session_id=session_id,
            session=session,
        )
        return payment_session

    async def get_session(self) -> Session:
        """
        Получение сессии для платежа
        """
        session = await self._get_session(
            user=self.user,
            coupon=self.coupon,
            basket=self.basket,
            products=self.products,
            session=self._session,
        )
        return session


async def add_product_basket(basket: Basket,
                             product: Product,
                             session: AsyncSession,
                             ) -> dict:
    check_frize_basket(basket=basket)
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


async def delete_product_basket(basket: Basket,
                                product: Product,
                                session: AsyncSession,
                                ) -> dict:
    check_frize_basket(basket=basket)
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
    check_frize_basket(basket=basket)
    basket.products.clear()
    await session.commit()
    return dict(state='success',
                detail='Basket is clear',
                )


def check_frize_basket(basket: Basket) -> None:
    """
    Проверка заморозки корзины
    В случае если на эту корзину существует
    не завершенная оплата
    """
    if basket.unique_temporary_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=dict(
                                    basket='В данный момент корзина '
                                    'имеет фиксированное состояние '
                                    'изза ожидающего платежа. '
                                    'Если вы хотите добавить товар, '
                                    'неоходимо отменить платеж.',
                                    ))
