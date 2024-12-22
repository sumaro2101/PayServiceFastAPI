from config.dao import BaseDAO
from config.models import User


class UserDAO(BaseDAO):
    """
    DAO пользователя
    """

    model = User
