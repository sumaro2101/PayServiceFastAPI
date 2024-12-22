from config.models import Basket
from config.dao import BaseDAO


class BasketDAO(BaseDAO):
    """
    DAO CRUD корзины
    """

    model = Basket
