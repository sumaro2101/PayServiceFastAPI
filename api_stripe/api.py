from datetime import datetime
import stripe
from typing import Any, List, Optional

from loguru import logger

from config.models import Product
from config.config import settings
from config.models.user import User
from .exeptions import (ErrorTypeProductStripe,
                        MultipleChoiseParamsError,
                        DoNotFindIDProductError,
                        )
from config.models import Product
from api_v1.auth.utils import get_hash_user, get_values_user
from api_v1.auth.hasher import UserPathHasher


class Stripe:
    """
    Страйп - платежная система
    Данный класс предназначен для обработки 
    """
    __key: str = settings.STRIPE.API_KEY

    def __init__(self,
                 product: Optional[Product],
                 update_params: Optional[dict] = None
                 ) -> None:
        if not isinstance(product, (Product | None)):
            raise ErrorTypeProductStripe(
                f'{product} - данный тип не может быть зарегистрированным',
                )
        if not isinstance(update_params, (dict | None)):
            raise ErrorTypeProductStripe(
                f'{update_params} - должен быть словарем ключ: значение',
                )
        if product and update_params:
            raise MultipleChoiseParamsError(
                'Необходимо указать только один из аргументов',
                )
        if not product and not update_params:
            raise MultipleChoiseParamsError(
                'Необходимо указать хотя бы один из аргументов',
            )
        stripe.api_key = self.__key
        self.product = product
        if self.product:
            self._id = self.product.id
            self._name = self.product.name
            self._price = self.product.price * 100
            self._active = self.product.is_active
            self._description = 'default'
        if update_params:
            self._update_params = update_params.copy()
            if not self._check_id():
                raise DoNotFindIDProductError('Не указан ID')

    async def _search_price(self,
                            id: int,
                            ) -> stripe.Price:
        """
        Поиск цены продукта
        """
        get_price = await stripe.Price.search_async(
                query=f'product:"{id}" AND active: "true"',
                )
        return get_price

    async def _search_product(self,
                              name: str,
                              ) -> Optional[stripe.Price]:
        """
        Поиск продукта из системы Stripe
        """
        get_product = await stripe.Product.search_async(
            query=f'name~"{name}"',
            )
        if get_product:
            id_ = get_product.data[0].id
            price = await self._search_price(id=id_)
            return price

    def _get_descriptions_item(self,
                               product: Product,
                               ) -> str:
        """
        Получение описания продукта
        """
        description = product.description
        return description if description else self._description

    async def _create_product(self,
                              id: int,
                              name: str,
                              description: str,
                              active: bool
                              ) -> stripe.Product:
        """
        Создание продукта на площадке Stripe
        """
        created_product = await stripe.Product.create_async(
            id=id,
            name=name,
            description=description,
            active=active,
            type='good',
        )
        return created_product

    async def _create_price(self,
                            product: stripe.Product,
                            price: int) -> stripe.Price:
        """
        Создание цены для продукта
        """
        created_price = await stripe.Price.create_async(
            unit_amount=price,
            currency='rub',
            product=product.id,
        )
        return created_price

    def _check_id(self):
        return 'id' in self._update_params.keys()

    def _check_price(self):
        return 'price' in self._update_params.keys()

    async def _update_product(self,
                              id: int,
                              params_update: dict
                              ) -> stripe.Product:
        """
        Обновление продукта
        """
        updated_product = await stripe.Product.modify_async(
            id=str(id),
            **params_update
        )
        return updated_product

    @logger.catch(reraise=True)
    async def _update_price(self,
                            product: stripe.Product,
                            id: str,
                            price: int,
                            ) -> stripe.Price:
        """
        Обновление цены на продукт
        """
        updated_price = await stripe.Price.modify_async(
            id=id,
            active=False,
        )
        await self._create_price(
            product=product,
            price=price * 100
        )
        return updated_price

    async def get_by_name(self):
        """
        Получение продукта по Имени
        """
        price = await self._search_product(
            name=self._name,
        )
        return price

    async def get_by_id(self):
        """
        Получение продукта по ID
        """
        price = await self._search_price(
            id=self._id,
        )
        return price

    async def update(self) -> None:
        """
        Обновление продукта
        """
        id_ = self._update_params.pop('id')
        if self._check_price():
            price = self._update_params.pop('price')
        product = await self._update_product(
            id=id_,
            params_update=self._update_params
        )
        prod_price = await self._search_price(id=product.id)
        await self._update_price(
            product=product,
            id=prod_price.data[0].id,
            price=price,
        )

    async def register(self):
        """
        Регистрация продукта в система Stripe
        """
        description = self._get_descriptions_item(self.product)
        product = await self._create_product(
            id=self._id,
            name=self._name,
            description=description,
            active=self._active,
        )
        price = await self._create_price(
            product=product,
            price=self._price,
        )
        return price


class StripeItems:
    """
    Класс отвечающий за множественные действия с сущностями Stripe
    """
    def __init__(self,
                 products: List[Product],
                 add_key: bool = False,
                 ) -> None:
        self._ids_products = list(products)
        if add_key:
            self.__add_key()

    @logger.catch(reraise=True)
    async def _get_products(self,
                            ids_products: List[Product],
                            ) -> stripe.ListObject:
        """
        Получение списка товаров
        """
        field_search = [product.id for product in ids_products]
        products = await stripe.Product.list_async(
            ids=field_search,
            type='good',
        )
        return products

    @logger.catch(reraise=True)
    async def _get_prices(self,
                          products: stripe.ListObject,
                          ) -> stripe.SearchResultObject:
        """
        Получение цен на товары
        """
        field_search = ' OR '.join([f'product:"{product.id}" AND active:"true"'
                                   for product
                                   in products.data])
        prices = await stripe.Price.search_async(query=field_search)
        return prices

    @logger.catch(reraise=True)
    async def get_list(self) -> stripe.SearchResultObject:
        """
        Получение списка цен на товары
        """
        products = await self._get_products(
            ids_products=self._ids_products,
        )
        logger.info(f'_get_products get {products}')
        prices = await self._get_prices(
            products=products,
        )
        logger.info(f'_get_prices get {prices}')
        return prices

    def __add_key(self):
        stripe.api_key = settings.STRIPE.API_KEY


class StripeSession:
    """
    Класс отвечающий за сессии Stripe
    """
    __key: str = settings.STRIPE.API_KEY

    def __init__(self,
                 user: User,
                 products: List[Product],
                 promo: Any = None
                 ) -> None:
        self.__user = user
        self._user_id = self.__user.id
        self._ids_products = products
        self._items = StripeItems(products=self._ids_products)
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
        url = self.__url + f'success/{path}'
        return url

    def _get_cancel_url(self) -> str:
        url = self.__url + f'cancel/'
        return url

    def _get_list_prices(self,
                         prices: stripe.SearchResultObject,
                         ) -> List[stripe.checkout.Session.CreateParamsLineItem]:
        list_prices = [
            stripe.checkout.Session.CreateParamsLineItem(
                price=price,
                quantity=1,
            )
            for price
            in prices.data
        ]
        return list_prices

    def _update_meta_ids(self,
                         products: List[Product],
                         ) -> dict[str, str]:
        ids = {str(product.id): str(product.id)
               for product
               in products}
        return ids

    async def _create_session_payment(self):
        """
        Создание сессии
        """
        prices: stripe.SearchResultObject = await self._items.get_list()
        list_prices = self._get_list_prices(prices=prices)
        success_url = self._get_success_url()
        ids = self._update_meta_ids(products=self._ids_products)
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

    async def get_session_payments(self):
        """
        Получение сессии для оплаты товаров
        """
        session = await self._create_session_payment()
        return session
