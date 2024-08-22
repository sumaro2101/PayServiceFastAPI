from pydantic import BaseModel, EmailStr
from typing import Annotated
from annotated_types import MaxLen, MinLen


class CreateUser(BaseModel):
    """Тело запроса для создания пользователя
    """
    username : Annotated[str, MinLen(3), MaxLen(50)]
    email: EmailStr
