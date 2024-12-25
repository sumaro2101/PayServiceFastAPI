from datetime import datetime
from pydantic import BaseModel


class ReadProducts(BaseModel):
    name: str
    price: int


class ReadCoupon(BaseModel):
    number: str
    discount: float


class ReadSuccessPayment(BaseModel):
    create_date: datetime
    coupon: ReadCoupon | None
    products: list[ReadProducts]
