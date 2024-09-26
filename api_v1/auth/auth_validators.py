from typing import Annotated
from fastapi import Depends, Form, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.utils import get_hash_password, check_password, decode_jwt
from api_v1.users.schemas import UserAuthSchema
from config.models import User, db_helper


# http_bearer = HTTPBearer()
oauth_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login/')


async def validate_auth_user(session: AsyncSession = Depends(db_helper.session_geter),
                            username: str = Form(),
                            password: str = Form(),
                            ) -> User | None:
    stmt = Select(User).where(User.username == username)
    result = list(await session.scalars(stmt))
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=dict(user='Не правильный логин или пароль'),
                            )
    if len(result) > 1:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=dict(user='Ошибка авторизации'))

    user = result[0]
    checked_password = check_password(password=password,
                                     hashed_password=user.password,
                                     )
    if not checked_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=dict(user='Не правильный логин или пароль'),
                            )

    if not user.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=dict(user='Пользователь отключен'))

    return user


def get_current_payload(credentials: Annotated[HTTPAuthorizationCredentials,
                                             Depends(oauth_scheme)],
                      ) -> UserAuthSchema:
    token = credentials
    try:
        payload = decode_jwt(token)
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=dict(token='Не правильный токен'),
                            )
    return payload


async def get_current_user(payload: dict = Depends(get_current_payload),
                            session: AsyncSession = Depends(db_helper.session_geter),
                            ):
    username = payload.get('username')
    stmt = Select(User).where(User.username == username)
    user = await session.scalar(stmt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=dict(user='Токен не верный'),
                            )

    return user


async def get_current_active_user(
    user: UserAuthSchema = Depends(get_current_user),
    ) -> User:
    if user.active:
        return user
    else:
        HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                      detail=dict(user='Пользователь не активный'))
