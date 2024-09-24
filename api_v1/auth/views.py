from fastapi import APIRouter, Depends

from api_v1.users.schemas import UserAuthSchema
from .utils import get_hash_password, check_password
from .schemas import TokenInfo


router = APIRouter(prefix='/auth',
                   tags=['AUTH'])

john = UserAuthSchema(username='John',
                      password=get_hash_password('qwerty12'),
                      )

users_db: dict[str, UserAuthSchema] = {
    john.username: john,
    }


@router.get('/login/',
            response_model=TokenInfo)
async def auth_user_issue_jwt(user: UserAuthSchema = Depends()):
    jwt_payload = dict(sub=user.username,
                       username=user.username,
                       email=user.email,
                       )
    access_token = get_hash_password()
    return TokenInfo(
        access_token=access_token,
        token_type='Bearer',
    )
