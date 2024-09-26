from pydantic import BaseModel, ConfigDict, Field
from typing import Union


class BasePostSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    title: str = Field(max_length=100)
    body: str = ''


class PostSchema(BasePostSchema):
    id: int


class PostCreateSchema(BasePostSchema):
    pass


class PostUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    title: Union[str, None] = Field(max_length=100,
                                    default=None,
                                    )
    body: Union[str, None] = Field(default=None)
