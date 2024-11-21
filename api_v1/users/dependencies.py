from typing import Annotated

from fastapi import HTTPException, Path, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.models import User
from config.database import db_connection
from . import crud


async def get_user_by_id(user_id: Annotated[int,
                                            Path(),
                                            ],
                         session: AsyncSession = Depends(db_connection.session_geter),
                         ) -> User:
    """ Получение пользователя по ID
    """
    user = await crud.get_user(session=session,
                               user_id=user_id,
                               )
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail=f'Пользователь {user_id} не был найден')


async def get_profile_by_id(profile_id: Annotated[int,
                                            Path(),
                                            ],
                            session: AsyncSession = Depends(db_connection.session_geter),
                            ) -> User:
    """ Получение профиля по ID
    """
    profile = await crud.get_profile(session=session,
                                     profile_id=profile_id,
                                     )
    if profile:
        return profile
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail=f'Профиль {profile_id} не был найден')
