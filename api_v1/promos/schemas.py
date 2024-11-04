from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field


class UserAssociationSchema(BaseModel):
    """
    Схема асоциации пользователя
    """

    model_config = ConfigDict(from_attributes=True)

    username: str
    email: str
    phone: str
    active: bool


class BaseCouponSchema(BaseModel):
    """
    Базовая схема купона
    """

    model_config = ConfigDict(from_attributes=True)

    discount: float = Field(gt=-1)
    number: str
    description: str
    active: bool = Field(default=True)
    end_at: datetime


class CouponSchemaCreate(BaseCouponSchema):
    """
    Схема создания купона
    """

    pass


class CouponSchemaUpdate(BaseModel):
    """
    Схема обновления купона
    """

    model_config = ConfigDict(from_attributes=True)

    number: str | None = Field(default=None)


class CouponSchema(BaseCouponSchema):
    """
    Полная схема купона
    """

    id: int
    create_at: datetime


class CouponViewSchema(CouponSchema):
    """
    Купон для Енд поинта
    """

    users: list[UserAssociationSchema]


class CouponAddCountUser(CouponSchema):
    """
    Схема добавления купона всем пользователям
    """
    users_count: int


class ActivityCouponeSchema(BaseCouponSchema):
    """
    Схема активности купона
    """
    
    pass
