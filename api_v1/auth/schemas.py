from datetime import datetime
from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    """
    Схема пользователя
    При добавлении полей в модель, так же
    необходимо добавить поля - тут!
    """
    username: str
    phone: str
    create_date: datetime


class UserCreate(schemas.BaseUserCreate):
    """
    Схема создания пользователя
    При добавлении полей в модель, так же
    необходимо добавить поля - тут!
    """
    username: str
    phone: str | None


class UserUpdate(schemas.BaseUserUpdate):
    """
    Схема обновления пользователя
    При добавлении полей в модель, так же
    необходимо добавить поля - тут!
    """
    username: str | None
    phone: str | None
