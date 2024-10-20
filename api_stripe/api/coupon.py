from loguru import logger
import stripe

from api_stripe.abs import Stripe
from api_stripe.exeptions import NotCorrectInputType, NotFindInputError
from api_stripe.types import TargetItem, StripeType
from api_stripe.handler import convert_date_to_unix_time
from config.config import settings


class CreateDiscountCoupon(Stripe):
    """
    Создание Stripe купона для скидок
    """
    __key: str = settings.STRIPE.API_KEY

    def __init__(self, target: TargetItem) -> None:
        self._discount = target.copy()
        stripe.api_key = self.__key

    def _correct_target(self, target: TargetItem) -> None:
        if not target:
            raise NotFindInputError('Не был указан объект для обработки')
        if not isinstance(target, dict):
            raise NotCorrectInputType(f'Ожидался тип словарь, не {target}')
        required_params = frozenset(('id', 'number', 'discount', 'end_at'))
        not_correct = required_params - target.keys()
        logger.info(f'check correct = {not_correct}')
        if not_correct:
            raise NotCorrectInputType(f'Не верные данные, не хватает аргументов {not_correct}')
        return

    async def _create_coupon(self, target: TargetItem) -> StripeType:
        self._correct_target(target=target)
        redeem = convert_date_to_unix_time(target['end_at'])
        meta = dict(id=str(target['id']))
        coupon = await stripe.Coupon.create_async(
            id=target['id'],
            duration='forever',
            percent_off=target['discount'],
            name=target['number'],
            metadata=meta,
            redeem_by=redeem,
        )
        return coupon

    async def action(self) -> StripeType:
        coupon = await self._create_coupon(
            target=self._discount,
        )
        return coupon


class UpdateDiscountCoupon(Stripe):
    """
    Обновление Stripe купона
    """
    __key: str = settings.STRIPE.API_KEY

    def __init__(self, target: TargetItem) -> None:
        self._discount = target.copy()
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
            raise NotCorrectInputType(
                f'Не верные данные, не хватает аргументов {not_correct}',
                )
        return

    async def _update_coupon(self, target: TargetItem) -> StripeType | None:
        self._correct_target(target=target)
        if 'number' not in target:
            return
        logger.info(f'get stripe discount update {target}')
        coupon = await stripe.Coupon.modify_async(
            id=str(target['id']),
            name=target['number'],   
        )
        return coupon

    async def action(self) -> StripeType | None:
        coupon = await self._update_coupon(
            target=self._discount,
        )
        return coupon


class DeleteDiscountCoupon(Stripe):
    """
    Удаление Stripe купона
    """
    __key: str = settings.STRIPE.API_KEY

    def __init__(self, target: TargetItem) -> None:
        self._discount = target.copy()
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
            raise NotCorrectInputType(
                f'Не верные данные, не хватает аргументов {not_correct}',
                )
        return

    async def _delete_coupon(self, target: TargetItem) -> None:
        self._correct_target(target=target)
        await stripe.Coupon.delete_async(
            sid=str(target['id']),
        )

    async def action(self) -> None:
        await self._delete_coupon(target=self._discount)
