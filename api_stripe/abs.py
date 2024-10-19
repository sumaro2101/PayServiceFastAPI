from abc import ABC, abstractmethod
from .types import TargerItem, StripeType


class Stripe(ABC):
    """
    Страйп - платежная система
    Данный класс определяет каркас
    """

    @abstractmethod
    def __init__(self,
                 target: TargerItem,
                 ) -> None:
        pass

    @abstractmethod
    def _correct_target(cls, target: TargerItem) -> None:
        pass

    @abstractmethod
    async def action(self) -> StripeType:
        pass