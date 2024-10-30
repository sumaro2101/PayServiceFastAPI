import stripe
from stripe import _error as error

from fastapi import HTTPException, status

from loguru import logger

from api_stripe.abs import Stripe
from api_stripe.exeptions import NotFindInputError, NotCorrectInputType
from api_stripe.types import TargetItem, StripeType, StipeResult
from api_stripe.handler import error_stripe_handle
from config.config import settings


class CreateStripeItem(Stripe):
    """
    Создание Stripe объекта
    """
    __key: str = settings.STRIPE.API_KEY

    def __init__(self, target: TargetItem) -> None:
        self._target = target.copy()
        stripe.api_key = self.__key

    def _correct_target(self, target: TargetItem) -> None:
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
                              target: TargetItem,
                              ) -> StripeType:
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

    def __init__(self, target: TargetItem) -> None:
        self._target = target.copy()
        stripe.api_key = self.__key

    def _correct_target(self, target: TargetItem) -> None:
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
                           target: TargetItem,
                           ) -> StripeType:
        updated_product = await stripe.Product.modify_async(
            id=str(id),
            **target
        )
        return updated_product

    async def _update_product(self,
                              target: TargetItem,
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

    def __init__(self, target: TargetItem) -> None:
        self._target = target.copy()
        stripe.api_key = self.__key

    def _correct_target(self, target: TargetItem) -> None:
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

    def __init__(self, target: TargetItem) -> None:
        self._target = target.copy()
        stripe.api_key = self.__key

    def _correct_target(self, target: TargetItem) -> None:
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
                              target: TargetItem,
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
