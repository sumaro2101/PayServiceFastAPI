from typing import Any
import jwt
import bcrypt
from datetime import timedelta, datetime, timezone

from fastapi import HTTPException, status

from config.models.user import User

from config.config import settings


def encode_jwt(payload: dict[str, Any],
                private_key: str | bytes = settings.AUTH_JWT.PRIVATE_KEY_PATH.read_text(encoding='UTF-8'),
                algorithm: str | None = settings.AUTH_JWT.ALGORITHM,
                expire: int = settings.AUTH_JWT.EXPIRE_MINUTES,
                expire_minutes: timedelta | None = None
                ):
    """
    JWT разкодировка ключа
    """
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_minutes:
        expire = now + expire_minutes
    else:
        expire = now + timedelta(minutes=expire)
    to_encode.update(
        exp=expire,
        iat=now,
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


def get_values_user(username: str,
                    create_date: datetime,
                    email: str) -> str:
    year = create_date.year
    mouth = create_date.month
    day = create_date.day
    hour = create_date.hour
    minute = create_date.minute
    second = create_date.second
    
    return f'{username}-{year}-{mouth}-{day}-{hour}-{minute}-{second}-{email}'


def get_hash_user(value: str) -> bytes:
    """Хеширование пользователя
    """
    salt = bcrypt.gensalt()
    value_bytes: bytes = value.encode(encoding='utf-8')
    return bcrypt.hashpw(password=value_bytes,
                         salt=salt,
                         )


def check_user(user: User,
               hashed_value: str,
               ) -> bool:
    """
    Проверка пользователя
    """
    username = user.username
    create_date = user.create_date
    email = user.email
    values = get_values_user(username=username,
                             create_date=create_date,
                             email=email,
                             )
    return bcrypt.checkpw(password=values.encode(encoding='utf-8'),
                          hashed_password=str(hashed_value).encode(encoding='utf-8'),
                          )


def check_password(password: str,
                   hashed_password: bytes,
                   ) -> bool:
    """
    Проверка пароля
    """
    return bcrypt.checkpw(password=str(password).encode('utf-8'),
                          hashed_password=hashed_password,
                          )


def check_type_token(token: str, type_token: str) -> None:
    if token and token != type_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=dict(user=f'Не верный тип токена, ожидался - {type_token}'),
                            )


def int_to_base36(i):
    """Convert an integer to a base36 string."""
    char_set = "0123456789abcdefghijklmnopqrstuvwxyz"
    if i < 0:
        raise ValueError("Negative base36 conversion input.")
    if i < 36:
        return char_set[i]
    b36 = ""
    while i != 0:
        i, n = divmod(i, 36)
        b36 = char_set[n] + b36
    return b36

def base36_to_int(s):
    """
    Convert a base 36 string to an int. Raise ValueError if the input won't fit
    into an int.
    """
    if len(s) > 13:
        raise ValueError("Base36 input too large")
    return int(s, 36)
