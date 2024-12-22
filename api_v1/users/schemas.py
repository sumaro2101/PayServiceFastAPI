from pydantic import BaseModel, Field, ConfigDict


class BaseProfileUser(BaseModel):
    """Базовое тело для профиля
    """
    model_config = ConfigDict(from_attributes=True)

    first_name: str | None = Field(max_length=40)
    last_name: str | None = Field(max_length=60)
    bio: str | None


class ProfileRead(BaseProfileUser):

    id: int


class ProfileCreateShema(BaseProfileUser):

    pass
