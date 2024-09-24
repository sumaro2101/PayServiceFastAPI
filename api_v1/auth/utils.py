import secrets
from typing import Annotated, Any
import jwt
import bcrypt

from fastapi import security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, Header

from .exeptions import UnauthedExpeption
from config.config import settings


def encode_jwt(payload: dict[str, Any],
                private_key: str | bytes = settings.AUTH_JWT.PRIVATE_KEY_PATH.read_text(encoding='UTF-8'),
                algorithm: str | None = settings.AUTH_JWT.ALGORITHM,
                expire: int = settings.AUTH_JWT.EXPIRE_MINUTES,
                ):
    """
    JWT разкодировка ключа
    """
    to_encode = payload.copy()
    expire = expire
    to_encode.update(
        exp=expire
    )
    encoded = jwt.encode(payload=to_encode,
                         key=private_key,
                         algorithm=algorithm,
                         )
    return encoded


def decode_jwt(jwt_key: str | bytes,
                key: str | bytes = settings.AUTH_JWT.PUBLIC_KEY_PATH.read_text(encoding='UTF-8'),
                algorithms: str = settings.AUTH_JWT.ALGORITHM,
                ):
    """
    JWT кодировка ключа
    """
    decoded = jwt.decode(jwt=jwt_key,
                         key=key,
                         algorithms=algorithms,
                         )
    return decoded


def get_hash_password(password: str) -> bytes:
    """
    Хеширование пароля
    """
    salt = bcrypt.gensalt()
    password_bytes: bytes = password.encode(encoding='UTF-8')
    return bcrypt.hashpw(password=password_bytes,
                         salt=salt,
                         )


def check_password(password: str,
                   hashed_password: bytes,
                   ) -> bool:
    """
    Проверка пароля
    """
    return bcrypt.checkpw(password=password,
                          hashed_password=hashed_password,
                          )


users_test = {
    '06d1fe67897493b302cb1ac264975b88592dfbfe1774fca36be3a68da9e1149a': 'admin',
}

security = HTTPBasic()


# def get_auth_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> str:
    
#     if credentials.username not in users_test:
#         raise UnauthedExpeption(detail=Settings.FAIL_BASIC_AUTH)

#     correct_password = users_test.get(credentials.username)

#     if not secrets.compare_digest(
#         credentials.password.encode('utf-8'),
#         correct_password.encode('utf-8')
#     ):
#         raise UnauthedExpeption(detail="Токен не валидный")

#     return credentials.username


def get_auth_user_static_token(
    auth_token: str = Header(alias='x-auth-token')
):
    if username := users_test.get(auth_token):
        return username
    raise UnauthedExpeption(detail="Токен не валидный")
