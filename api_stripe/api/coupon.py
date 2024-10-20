import stripe

from api_stripe.abs import Stripe
from api_stripe.types import TargetItem
from config.config import settings


class CreateDiscountPromo(Stripe):
    """
    Создание промо кода для скидок
    """
    __key: str = settings.STRIPE.API_KEY

    def __init__(self, target: TargetItem) -> None:
        self._discount = target.copy()
        stripe.api_key = self.__key
