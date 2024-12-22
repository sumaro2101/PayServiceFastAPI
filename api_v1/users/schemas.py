from pydantic import BaseModel, Field, ConfigDict
from api_v1.auth.schemas import UserRead


class BaseProfileUser(BaseModel):
    """Базовое тело для профиля
    """
    model_config = ConfigDict(from_attributes=True)

    first_name: str | None = Field(max_length=40)
    last_name: str | None = Field(max_length=60)
    bio: str | None


class ProfileShema(BaseProfileUser):

    id: int
    user: UserRead


class ProfileCreateShema(BaseProfileUser):

    pass
