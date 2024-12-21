from fastapi import Depends, HTTPException, status
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from api_v1.auth.hasher import UserPathHasher
from config.models import User
from config.database import db_connection


async def get_user_by_hash(uid: str,
                           token: str,
                           session: AsyncSession = Depends(db_connection.session_geter)):
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
