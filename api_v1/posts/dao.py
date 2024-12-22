from config.models import Post
from config.dao import BaseDAO


class PostDAO(BaseDAO):
    """
    DAO CRUD постов
    """

    model = Post
