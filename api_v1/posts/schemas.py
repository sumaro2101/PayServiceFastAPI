from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Union
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


class BasePostSchema(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(max_length=100)
    body: str = ''


class PostSchema(BasePostSchema):

    id: int
    user: UserRead


class PostsRead(BasePostSchema):

    id: int


class PostCreateSchema(BasePostSchema):

    pass


class PostUpdateSchema(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    title: Union[str, None] = Field(max_length=100,
                                    default=None,
                                    )
    body: Union[str, None] = Field(default=None)
