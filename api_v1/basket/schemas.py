from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import Url


class ProductSchema(BaseModel):
    name: str
    description: str
    price: int


class BaseBasketSchema(BaseModel):
    """Схема корзины
    """
    model_config = ConfigDict(from_attributes=True)

    products: list[ProductSchema]


class BasketSchema(BaseBasketSchema):
    id: int


class LinkToPayment(BaseModel):
    link: Url


class BasketView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    products: list[int] = Field(default_factory=list)


class CouponeNameSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    coupon_name: str | None = Field(default=None)
