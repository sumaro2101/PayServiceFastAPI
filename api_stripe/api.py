import stripe
import os
from typing import List, Optional
from loguru import logger

from config.models import Product
from config.config import settings
from .exeptions import (ErrorTypeProductStripe,
                        MultipleChoiseParamsError,
                        DoNotFindIDProductError,
                        )


class Stripe:
    """
    Страйп - платежная система
    Данный класс предназначен для обработки 
    """
    __key: str = settings.STRIPE.API_KEY

    def __init__(self,
                 product: Optional[Product],
                 update_params: Optional[dict]
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
    __key: str = settings.STRIPE.API_KEY

    def __init__(self,
                 *products: List[int],
                 ) -> None:
        self._ids_products = list(products)
        stripe.api_key = self.__key

    async def _get_prices(self,
                          ids_products: List[int],
                          ) -> stripe.SearchResultObject:
        """
        Получение цен на товары
        """
        field_search = ' AND '.join([f'product:{product.id}'
                                   for product
                                   in ids_products.data])
        prices = await stripe.Price.search_async(query=field_search)
        return prices

    @logger.catch(reraise=True)
    async def get_list(self):
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
