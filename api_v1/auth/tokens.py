from pydantic import BaseModel, ConfigDict
from api_v1.auth.utils import encode_jwt

from typing import ClassVar

from config.config import settings
from config.models.user import User


t_type = settings.AUTH_JWT.TOKEN_TYPE_FIELD


class Token(BaseModel):
    """
    Класс токена

    Преназначен для выпуска access токена
    и для refresh токена
    """
    model_config = ConfigDict(arbitrary_types_allowed=True,
                              frozen=True,
                              )

    __name_type: ClassVar[str] = t_type
    __access_token: ClassVar[str] = settings.AUTH_JWT.ACCESS_TOKEN_TYPE
    __refresh_token: ClassVar[str] = settings.AUTH_JWT.REFRESH_TOKEN_TYPE
    __expite_access_token: ClassVar[int] = settings.AUTH_JWT.EXPIRE_MINUTES
    __expire_refresh_token: ClassVar[int] = settings.AUTH_JWT.REFRESH_EXPIRE_MINUTES

    user: User

    def _create_jwt(self,
                    token_type: str,
                    payload: dict[str],
                    expire: int,
                    ) -> str:
        """
        Создание jwt токена
        """
        jwt_payload = {self.__name_type: token_type}
        jwt_payload.update(payload)
        token = encode_jwt(jwt_payload, expire=expire)
        return token

    def create_access_token(self) -> str:
        """
        Создание access токена
        """
        jwt_payload = dict(sub=self.user.username,
                           username=self.user.username,
                           email=self.user.email,
                           )
        access_token = self._create_jwt(token_type=self.__access_token,
                                        payload=jwt_payload,
                                        expire=self.__expite_access_token,
                                        )
        return access_token

    def create_refresh_token(self) -> str:
        """
        Создание refresh токена
        """
        jwt_payload = dict(sub=self.user.username)
        refresh_token = self._create_jwt(token_type=self.__refresh_token,
                                         payload=jwt_payload,
                                         expire=self.__expire_refresh_token,
                                         )
        return refresh_token
