from fastapi import APIRouter, Depends
from config.models.user import User
from .schemas import TokenInfo
from .auth_validators import validate_auth_user, get_access_of_refresh
from .tokens import Token


router = APIRouter(prefix='/auth',
                   tags=['Auth'])


@router.post('/login/',
            response_model=TokenInfo,
            )
async def auth_user_issue_jwt(user: User = Depends(validate_auth_user)):
    token = Token(user=user)
    access_token = token.create_access_token()
    refresh_token = token.create_refresh_token()
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post('/token/refresh/',
             response_model=TokenInfo,
             response_model_exclude_none=True,
             )
async def refresh_token_jwt_view(user: User = Depends(get_access_of_refresh)):
    token = Token(user=user)
    access_token = token.create_access_token()
    return TokenInfo(
        access_token=access_token,
    )
