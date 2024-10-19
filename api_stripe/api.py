import stripe
from stripe import _error as error
from typing import Any, List

from loguru import logger

from fastapi import status, HTTPException

from config.models import Product
from config.config import settings
from config.models.user import User
from .exeptions import (NotFindInputError,
                        NotCorrectInputType,
                        )
from config.models import Product
from api_v1.auth.hasher import UserPathHasher
from .abs import Stripe
from .types import (TargerItem,
                    StripeType,
                    StipeResult,
                    SessionParams,
                    Session,
                    )
from .handler import error_stripe_handle


class CreateStripeItem(Stripe):
    """
    Создание Stripe объекта
    """
    __key: str = settings.STRIPE.API_KEY

    def __init__(self, target: TargerItem) -> None:
        self._target = target.copy()
        stripe.api_key = self.__key

    def _correct_target(self, target: TargerItem) -> None:
        if not target:
            raise NotFindInputError('Не был указан объект для обработки')
        if not isinstance(target, dict):
            raise NotCorrectInputType(f'Ожидался тип словарь, не {target}')
        required_params = frozenset(('id', 'name', 'price'))
        not_correct = required_params - target.keys()
        logger.info(f'check correct = {not_correct}')
        if not_correct:
            raise NotCorrectInputType(f'Не верные данные, не хватает аргументов {not_correct}')
        return

    async def _create_product(self,
                              target: TargerItem,
                              ) -> stripe.Price:
        """
        Создание цены для продукта
        """
        self._correct_target(target=target)
        meta_data = dict(id=target['id'])
        product_value = stripe.Price.CreateParamsProductData(
            active=True,
            id=target['id'],
            name=target['name'],
            metadata=meta_data,
        )
        created_price = await stripe.Price.create_async(
            unit_amount=target['price'] * 100,
            currency='rub',
            product_data=product_value,
            metadata=meta_data,
        )
        return created_price

    async def action(self):
        """
        Регистрация продукта в системе Stripe
        """
        logger.info(f'product = {self._target}')
        price = await self._create_product(
            target=self._target,
        )
        return price


class UpdateStripeItem(Stripe):
    """
    Обновление Stripe объекта
    """
    __key: str = settings.STRIPE.API_KEY

    def __init__(self, target: TargerItem) -> None:
        self._target = target.copy()
        stripe.api_key = self.__key

    def _correct_target(self, target: TargerItem) -> None:
        if not target:
            raise NotFindInputError('Не был указан объект для обработки')
        if not isinstance(target, dict):
            raise NotCorrectInputType(f'Ожидался тип словарь, не {target}')
        required_params = frozenset(('id',))
        not_correct = required_params - target.keys()
        logger.info(f'check correct = {not_correct}')
        if not_correct:
            raise NotCorrectInputType(f'Не верные данные, не хватает аргументов {not_correct}')
        return

    @logger.catch(reraise=True)
    async def _search_price(self,
                            id: int,
                            ) -> StripeType:
        """
        Поиск цены продукта
        """
        get_price = await stripe.Price.search_async(
                query=f'metadata["id"]:"{id}" AND active: "true"',
                )
        logger.info(f'get_price = {get_price}')
        return get_price
    
    async def _create_price(self,
                            product_id:int,
                            price: int,
                            ):
        meta = dict(id=product_id)
        prefetch_create = await stripe.Price.create_async(
            active=True,
            currency='rub',
            metadata=meta,
            product=product_id,
            unit_amount=price,
        )
        return prefetch_create

    @logger.catch(reraise=True)
    async def _deactivate_price(self,
                            id: str,
                            ) -> StripeType:
        """
        Обновление цены на продукт
        """
        updated_price = await stripe.Price.modify_async(
            id=str(id),
            active=False,
        )
        return updated_price
    
    async def _update_item(self,
                           id:int,
                           target: TargerItem,
                           ) -> StripeType:
        updated_product = await stripe.Product.modify_async(
            id=str(id),
            **target
        )
        return updated_product

    async def _update_product(self,
                              target: TargerItem,
                              ) -> StripeType:
        """
        Обновление продукта
        """
        self._correct_target(target=target)
        id_ = target.pop('id')
        if 'price' in target.keys():
            price = target.pop('price')
            logger.info(f'id = {id_}')
            prod_price = await self._search_price(id=id_)
            await self._deactivate_price(
                id=prod_price.data[0].id,
            )
            await self._create_price(
                product_id=id_,
                price=price * 100
            )
        logger.info(f'len target = {len(target)}')
        if len(target) > 0:
            product = await self._update_item(
                id=id_,
                target=target
            )
            return product

    async def action(self) -> StripeType:
        """
        Обновление продукта
        """
        return await self._update_product(
            target=self._target,
        )


class ActivateStipeItem(Stripe):
    """
    Активация Stripe объекта
    Активирует объект и последнюю цену
    """
    __key: str = settings.STRIPE.API_KEY
    def __init__(self, target: TargerItem) -> None:
        self._target = target.copy()
        stripe.api_key = self.__key

    def _correct_target(self, target: TargerItem) -> None:
        if not target:
            raise NotFindInputError('Не был указан объект для обработки')
        if not isinstance(target, dict):
            raise NotCorrectInputType(f'Ожидался тип словарь, не {target}')
        required_params = frozenset(('id',))
        not_correct = required_params - target.keys()
        logger.info(f'check correct = {not_correct}')
        if not_correct:
            raise NotCorrectInputType(f'Не верные данные, не хватает аргументов {not_correct}')
        return
    
    async def _activate_item(self,
                             id: int,
                             ) -> StripeType:
        product = await stripe.Product.modify_async(
            id=str(id),
            active=True,
        )
        return product

    async def _search_prices(self,
                             id: int,
                             ) -> StipeResult:
        meta = f'metadata["id"]:"{id}"'
        prices = await stripe.Price.search_async(
            query=meta,
        )
        return prices.data

    async def _activate_last_price(self,
                                   prices: StipeResult,
                                   ) -> StripeType:
        last_price = prices[0]
        await stripe.Price.modify_async(
            id=last_price.id,
            active=True,
        )

    async def _activate_product(self,
                                target: StripeType,
                                ):
        self._correct_target(target=target)
        await self._activate_item(
            id=target['id'],
        )
        prices = await self._search_prices(
            id=target['id'],
        )
        await self._activate_last_price(
            prices=prices,
        )

    async def action(self):
        """Активация продукта
        """
        await self._activate_product(
            target=self._target,
        )


class DeactivateStripeItem(Stripe):
    """
    Деактивация Stripe объекта
    """
    __key: str = settings.STRIPE.API_KEY

    def __init__(self, target: TargerItem) -> None:
        self._target = target.copy()
        stripe.api_key = self.__key

    def _correct_target(self, target: TargerItem) -> None:
        if not target:
            raise NotFindInputError('Не был указан объект для обработки')
        if not isinstance(target, dict):
            raise NotCorrectInputType(f'Ожидался тип словарь, не {target}')
        required_params = frozenset(('id',))
        not_correct = required_params - target.keys()
        logger.info(f'check correct = {not_correct}')
        if not_correct:
            raise NotCorrectInputType(f'Не верные данные, не хватает аргументов {not_correct}')
        return

    @logger.catch(reraise=True)
    async def _search_price(self,
                            id: int,
                            ) -> StripeType:
        """
        Поиск цены продукта
        """
        logger.info(f'search_price by {id}')
        get_price = await stripe.Price.search_async(
                query=f'metadata["id"]:"{id}" AND active: "true"',
                )
        logger.info(f'get_price = {get_price}')
        return get_price

    async def _deactivate_price(self,
                            price_id: int,
                            ) -> None:
        await stripe.Price.modify_async(
            id=str(price_id),
            active=False,
        )

    async def _deactivate_item(self,
                          id: int,
                          ) -> None:
        await stripe.Product.modify_async(
            id=str(id),
            active=False,
        )

    async def _deactivate_product(self,
                              target: TargerItem,
                              ) -> None:
        self._correct_target(target=target)
        price = await self._search_price(id=target['id'])
        price_list = price.data
        [await self._deactivate_price(
            price_id=price.id,
            )
         for price
         in price_list]
        await self._deactivate_item(
            id=target['id']
        )

    async def action(self) -> StripeType:
        """
        Деактивация продукта
        """
        try:
            return await self._deactivate_product(
                target=self._target,
            )
        except error.InvalidRequestError as err:
            stripe_error = error_stripe_handle(err=err)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=dict(stripe=stripe_error,
                                            product='Product has been deleted in server',
                                            ),
                                )


class StripeItems:
    """
    Класс отвечающий за множественные действия с сущностями Stripe
    """
    def __init__(self,
                 products: List[Product],
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
        self._products = products
        self._items = StripeItems(products=self._products)
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
