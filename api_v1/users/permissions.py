from fastapi import HTTPException, status, Depends

from api_v1.auth.auth_validators import get_current_active_user
from config.models.user import User
from .dependencies import get_user_by_id


async def authenticate(
    current_user: User = Depends(get_current_active_user),
    ) -> User:
    """
    Проверка аунтифицированного пользователя
    """
    return current_user


async def is_current_user(
    current_user: User = Depends(get_current_active_user),
    target: User = Depends(get_user_by_id)
    ) -> User:
    """
    Проверка принадлежности сущности к текущему пользователю
    """
    if not current_user == target:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=dict(user='У вас нет прав на это действие'),
                            )
    return target
