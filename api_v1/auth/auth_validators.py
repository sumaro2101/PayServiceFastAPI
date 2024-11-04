from typing import Annotated
from fastapi import Depends, Form, status, HTTPException
from fastapi.security import (HTTPBearer,
                              HTTPAuthorizationCredentials,
                              OAuth2PasswordBearer,
                              )
from jwt import InvalidTokenError
from sqlalchemy import Select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from loguru import logger

from api_v1.auth.utils import check_password, decode_jwt, check_type_token
from api_v1.auth.hasher import UserPathHasher
from api_v1.users.schemas import UserAuthSchema
from config.models import User, db_helper
from config.config import settings


http_bearer = HTTPBearer()
oauth_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login/')


async def get_user_by_hash(uid: str,
                           token: str,
                           session: AsyncSession = Depends(db_helper.session_geter)):
    user_id = int(UserPathHasher.urlsafe_base64_decode(uid=uid).decode())
    logger.info(f'user_id = {user_id}')
    stmt = Select(User).where(User.id == user_id)
    user: User = await session.scalar(statement=stmt)
    path_hasher = UserPathHasher(user=user)
    if path_hasher.check_token(token=token):
        return user
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=dict(permission='Доступ запрещен'))


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
                                             Depends(http_bearer)],
                      ) -> UserAuthSchema:
    token = credentials.credentials
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
    token_type = payload.get(settings.AUTH_JWT.TOKEN_TYPE_FIELD)
    check_type_token(token_type, settings.AUTH_JWT.ACCESS_TOKEN_TYPE)
    username = payload.get('username')
    stmt = Select(User).where(User.username == username).options(selectinload(User.coupons))
    user = await session.scalar(stmt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=dict(user='Токен не верный'),
                            )

    return user


async def get_access_of_refresh(payload: dict = Depends(get_current_payload),
                                session: AsyncSession = Depends(db_helper.session_geter),
                                ):
    token_type = payload.get(settings.AUTH_JWT.TOKEN_TYPE_FIELD)
    check_type_token(token_type, settings.AUTH_JWT.REFRESH_TOKEN_TYPE)
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
