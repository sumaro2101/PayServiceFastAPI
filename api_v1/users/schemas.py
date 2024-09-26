from typing import Union, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Annotated
from annotated_types import MaxLen, MinLen


class BaseUserSchema(BaseModel):
    """Тело запроса для создания пользователя
    """
    model_config = ConfigDict(from_attributes=True)

    username : Annotated[str, MinLen(3), MaxLen(50)]
    phone: Union[str, None] = Field(default=None)
    email: EmailStr
    active: bool = True


class BaseProfileUser(BaseModel):
    """Базовое тело для профиля
    """
    model_config = ConfigDict(from_attributes=True)
    
    first_name: Optional[str] = Field(max_length=40)
    last_name: Optional[str] = Field(max_length=60)
    bio: Optional[str]


class UserUpdateSchema(BaseModel):
    """Тело запроса для обновления пользователя
    """
    model_config = ConfigDict(from_attributes=True)

    username : Union[Annotated[str, MinLen(3), MaxLen(50)], None] = Field(default=None)
    phone: Union[str, None] = Field(default=None)
    email: Union[EmailStr, None] = Field(default=None)


class UserCreateSchema(BaseUserSchema):
    """Тело запроса для создания пользователя
    """

    password1: str
    password2: str


class UserAuthSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    username: str
    password: bytes
    email: EmailStr | None = None
    active: bool = True


class UserSchema(BaseUserSchema):

    id: int


class ProfileShema(BaseProfileUser):
    
    id: int


class ProfileCreateShema(BaseProfileUser):
    pass
