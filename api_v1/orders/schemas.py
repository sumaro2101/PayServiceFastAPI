from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReadCoupon(BaseModel):
    number: str
    discount: float


class ReadProducts(BaseModel):
    id: int
    name: str
    price: int


class OrderCreateSchema(BaseModel):

    coupon_name: str | None = Field(default=None)
    products: list[int]


class ReadOrder(BaseModel):
    id: int
    create_date: datetime
    coupon: ReadCoupon | None
    products: list[ReadProducts]


class OrderUpdateSchema(BaseModel):

    coupon_name: Optional[str] = Field(default=None)
    products: Optional[list[int]] = Field(default=None)
