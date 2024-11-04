from pydantic import BaseModel, ConfigDict, Field


class BaseBasketSchema(BaseModel):
    """Схема корзины
    """
    model_config = ConfigDict(from_attributes=True)
    
    user_id: int
    products: list[int] = Field(default_factory=list)


class BasketSchema(BaseBasketSchema):
    id: int

 
class BasketView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    products: list[int] = Field(default_factory=list)


class CouponeNameSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    number: str | None = Field(default=None)
