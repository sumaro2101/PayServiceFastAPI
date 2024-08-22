from pydantic import BaseModel, EmailStr


class CreateUser(BaseModel):
    """Тело запроса для создания пользователя
    """
    email: EmailStr
