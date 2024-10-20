from typing import Any
import stripe

from loguru import logger

from config.config import settings
from config.models import Product, User
from api_stripe.api import StripeItems
from api_stripe.types import StipeResult, SessionParams, Session
from api_v1.auth.hasher import UserPathHasher


class StripeSession:
    """
    Класс отвечающий за сессии Stripe
    """
    __key: str = settings.STRIPE.API_KEY

    def __init__(self,
                 user: User,
                 products: list[Product],
                 unique_code: str,
                 promo: Any = None
                 ) -> None:
        self.__user = user
        self._user_id = self.__user.id
        self._products = products
        self._items = StripeItems(products=self._products)
        self._unique_code = unique_code
        self._promo = promo
        self.__url = r'http://localhost:8080/api/v1/payments/'
        stripe.api_key = self.__key

    def _get_discount_promo(self,
                            promo: Any,
                            ) -> stripe.checkout.Session.CreateParamsDiscount:
        pass

    def _get_success_url(self) -> str:
        path_hasher = UserPathHasher(user=self.__user)
        path = path_hasher.make_url_token()
        url = self.__url + f'success/{path}/{self._unique_code}/'
        return url

    def _get_cancel_url(self) -> str:
        url = self.__url + f'cancel/'
        return url

    def _get_list_prices(self,
                         prices: StipeResult,
                         ) -> SessionParams:
        list_prices = [
            stripe.checkout.Session.CreateParamsLineItem(
                price=price,
                quantity=1,
            )
            for price
            in prices
            if price.active
        ]
        return list_prices

    def _update_meta_ids(self,
                         products: list[Product],
                         ) -> dict[str, str]:
        ids = {str(product.id): str(product.id)
               for product
               in products}
        return ids

    async def _create_session_payment(self) -> Session:
        """
        Создание сессии
        """
        prices: StipeResult = await self._items.get_list()
        list_prices = self._get_list_prices(prices=prices)
        success_url = self._get_success_url()
        ids = self._update_meta_ids(products=self._products)
        logger.info(f'_create_session_payment success_url - \n{success_url}')
        return_url = self._get_cancel_url()
        params = dict(currency='rub',
                      line_items=list_prices,
                      mode='payment',
                      submit_type='pay',
                      metadata=dict(user_id=str(self._user_id)) | ids,
                      success_url=success_url,
                      cancel_url=return_url,
                      )
        logger.info(f'_create_session_payment params - \n{params}')
        if self._promo:
            promo = self._get_discount_promo()
            params.update(discounts=promo)
            params['metadata'].update(promo=promo.coupon)
        created_session = await stripe.checkout.Session.create_async(
            **params
        )
        return created_session

    async def get_session_payments(self) -> Session:
        """
        Получение сессии для оплаты товаров
        """
        session = await self._create_session_payment()
        return session
