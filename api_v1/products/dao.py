from config.models import Product
from config.dao import BaseDAO


class ProductDAO(BaseDAO):
    """
    DAO CRUD товара
    """

    model = Product
