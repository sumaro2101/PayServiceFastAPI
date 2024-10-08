from pydantic import BaseModel, ConfigDict, Field


class BaseBasketSchema(BaseModel):
    """Схема корзины
    """
    model_config = ConfigDict()
    
    user_id: int
    products: list[int] = Field(default_factory=list)


class BasketSchema(BaseBasketSchema):
    id: int

 
class BasketView(BaseModel):
    model_config = ConfigDict()

    products: list[int] = Field(default_factory=list)
