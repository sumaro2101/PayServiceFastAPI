import stripe

from loguru import logger

from config.models import Product
from config.config import settings
from api_stripe.types import StipeResult


class StripeItems:
    """
    Класс отвечающий за множественные действия с сущностями Stripe
    """
    def __init__(self,
                 products: list[Product],
                 add_key: bool = False,
                 ) -> None:
        self._products = list(products)
        if add_key:
            self.__add_key()

    @logger.catch(reraise=True)
    async def _get_prices(self,
                          products: list[Product],
                          ) -> StipeResult:
        """
        Получение цен на товары
        """
        field_search = ' OR '.join([f'metadata["id"]:"{product.id}"'
                                   for product
                                   in products])
        logger.info(f'search_fields = {field_search}')
        prices = await stripe.Price.search_async(query=field_search)
        return prices

    @logger.catch(reraise=True)
    async def get_list(self) -> StipeResult:
        """
        Получение списка цен на товары
        """
        prices = await self._get_prices(
            products=self._products,
        )
        logger.info(f'_get_prices get {prices}')
        return prices.data

    def __add_key(self):
        stripe.api_key = settings.STRIPE.API_KEY
