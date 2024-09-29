from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class BaseOrderSchema(BaseModel):
    model_config = ConfigDict()
    
    promocode: Optional[str] = Field(default=None)
    products: list[int]


class OrderCreateSchema(BaseOrderSchema):
    pass


class OrderUpdateSchema(BaseModel):
    model_config = ConfigDict()

    promocode: Optional[str] = Field(default=None)
    products: Optional[list[int]] = Field(default=None)
