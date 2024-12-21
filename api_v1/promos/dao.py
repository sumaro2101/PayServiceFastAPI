from config.dao import BaseDAO
from config.models import Coupon


class PromoDAO(BaseDAO):
    """
    DAO для купонов
    """

    model = Coupon
