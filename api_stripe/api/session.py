import stripe

from loguru import logger

from config.config import settings
from config.models import Product, User
from api_stripe.api import StripeItems
from api_stripe.types import StipeResult, SessionParams, Session, StripeType
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
                 promo: int | None = None
                 ) -> None:
        self.__user = user
        self._user_id = self.__user.id
        self._products = products
        self._items = StripeItems(products=self._products)
        self._unique_code = unique_code
        self._promo = promo
        self.__url = r'http://localhost:8080/api/v1/payments/'
        self.__path = None
        stripe.api_key = self.__key

    def _set_hash_user_path(self):
        path_hasher = UserPathHasher(user=self.__user)
        self.__path = path_hasher.make_url_token()
        return self.__path

    def _get_discount_promo(self,
                            promo: int,
                            ) -> list[stripe.checkout.Session.CreateParamsDiscount]:
        return [stripe.checkout.Session.CreateParamsDiscount(
            coupon=str(promo),
        ),]

    def _get_success_url(self) -> str:
        url = self.__url + f'success/{self.__path}/{self._unique_code}/'
        return url

    def _get_cancel_url(self) -> str:
        url = self.__url + f'cancel/{self.__path}/{self._unique_code}/'
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

    @logger.catch(reraise=True)
    async def _create_session_payment(self) -> Session:
        """
        Создание сессии
        """
        prices: StipeResult = await self._items.get_list()
        list_prices = self._get_list_prices(prices=prices)
        self._set_hash_user_path()
        success_url = self._get_success_url()
        return_url = self._get_cancel_url()
        logger.debug(f'_create_session_payment success_url - \n{success_url}')
        params = dict(currency='rub',
                      line_items=list_prices,
                      mode='payment',
                      submit_type='pay',
                      metadata=dict(user_id=str(self._user_id),
                                    id=self._unique_code,
                                    ),
                      payment_method_types=['card'],
                      success_url=success_url,
                      cancel_url=return_url,
                      )
        logger.info(f'_create_session_payment params - \n{params}')
        if self._promo:
            logger.debug(f'get promo {self._promo}')
            promo = self._get_discount_promo(promo=self._promo)
            logger.debug(f'ready to send promo {promo}')
            params.update(discounts=promo)
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


class ExpireSession:
    """
    Класс отмены сессии платежа
    """
    __key: str = settings.STRIPE.API_KEY

    def __init__(self,
                 session_id: int,
                 ) -> None:
        self._session_id = session_id
        stripe.api_key = self.__key

    async def _expire_session(self,
                              session_id: int,
                              ) -> None:
        stripe.checkout.Session.expire_async(
            session=session_id,
        )
        logger.info(f'checkout is been deleted {session_id}')

    async def expire_session(self) -> None:
        """
        Отмена сессии
        """
        await self._expire_session(self._session_id)
