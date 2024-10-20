from datetime import datetime
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
    nubmer: str
    description: str
    active: bool = Field(default=True)
    end_at: datetime = Field(gt=datetime.now())


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

    discount: float | None = Field(gt=-1, default=None)
    nubmer: str | None = Field(default=None)
    description: str | None = Field(default=None)
    active: bool | None = Field(default=None)
    end_at: datetime | None = Field(default=None, gt=datetime.now())


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


class ActivityCouponeSchema(BaseCouponSchema):
    """
    Схема активности купона
    """
    
    pass
