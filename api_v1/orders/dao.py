from config.models import Order
from config.dao import BaseDAO


class OrderDAO(BaseDAO):
    """
    DAO CRUD заказа
    """

    model = Order
