from fastapi import APIRouter, Depends

from api_v1.users.schemas import UserAuthSchema
from .schemas import TokenInfo
from .auth_validators import validate_auth_user
from .tokens import Token


router = APIRouter(prefix='/auth',
                   tags=['AUTH'])


@router.post('/login/',
            response_model=TokenInfo,
            )
async def auth_user_issue_jwt(user: UserAuthSchema = Depends(validate_auth_user),
                              ):
    token = Token(user=user)
    access_token = token.create_access_token()
    refresh_token = token.create_refresh_token()
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token
    )
