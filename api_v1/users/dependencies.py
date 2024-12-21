from typing import Annotated

from fastapi import HTTPException, Path, Depends, status
from fastapi_users import BaseUserManager, models, exceptions
from sqlalchemy.ext.asyncio import AsyncSession

from config.models import User
from . import crud
from .user_manager import get_user_manager


async def get_profile_by_id(user_id: Annotated[int,
                                                  Path(),
                                                  ],
                            session: AsyncSession,
                            ) -> User:
    """
    Получение профиля по ID
    """
    profile = await crud.get_profile(session=session,
                                     user_id=user_id,
                                     )
    if profile:
        return profile
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'Profile {user_id} not found',
                        )


async def get_user_or_404(
    id: str,
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
) -> models.UP:
    try:
        parsed_id = user_manager.parse_id(id)
        return await user_manager.get(parsed_id)
    except (exceptions.UserNotExists, exceptions.InvalidID) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found',
                            ) from e
