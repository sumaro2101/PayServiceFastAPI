from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.users.schemas import UserAuthSchema
from .utils import get_hash_password, encode_jwt
from .schemas import TokenInfo
from .auth_validators import validate_auth_user


router = APIRouter(prefix='/auth',
                   tags=['AUTH'])


@router.post('/login/',
            response_model=TokenInfo,
            )
async def auth_user_issue_jwt(user: UserAuthSchema = Depends(validate_auth_user),
                              ):
    jwt_payload = dict(sub=user.username,
                       username=user.username,
                       email=user.email,
                       )
    access_token = encode_jwt(jwt_payload)
    return TokenInfo(
        access_token=access_token,
        token_type='Bearer',
    )
