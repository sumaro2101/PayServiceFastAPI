from fastapi import APIRouter, Depends, status, HTTPException

from fastapi_users import FastAPIUsers
from fastapi_users.router.common import ErrorModel
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.schemas import UserRead, UserUpdate
from api_v1.users.user_manager import get_user_manager
from config.models import User
from config.database import db_connection
from .schemas import ProfileCreateShema, ProfileRead
from . import crud
from .dao import UserDAO
from .dependencies import get_profile_by_id
from .common import ErrorCode
from api_v1.auth import auth_backend, active_user, superuser


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    (auth_backend,)
)


router = APIRouter(prefix='/users',
                   tags=['Users'],
                   )


@router.get('',
            name='users:get_users_list',
            response_model=list[UserRead],
            dependencies=[Depends(superuser)],
            responses={
                status.HTTP_401_UNAUTHORIZED: {
                    "description": "Missing token or inactive user.",
                },
                status.HTTP_403_FORBIDDEN: {
                    "description": "Not a superuser.",
                },
            },
            )
async def get_list_user_api_view(
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await UserDAO.find_all_items_by_args(
        session=session,
        one_to_many=(User.profile,),
        many_to_many=(User.orders, User.coupons),
    )


# profile
@router.post('/profile/create',
             name='users:profile_create',
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(active_user)],
             response_model=ProfileRead,
             responses={
                 status.HTTP_401_UNAUTHORIZED: {
                    "description": "Missing token or inactive user.",
                 },
                 status.HTTP_400_BAD_REQUEST: {
                     'model': ErrorModel,
                     'content': {
                         'application/json': {
                             'examples': {
                                 ErrorCode.PROFILE_IS_ALREADY_EXISTS: {
                                     'summary': 'Current user is already have profile',
                                     'value': {
                                         'detail': ErrorCode.PROFILE_IS_ALREADY_EXISTS,
                                     }
                                 }

                             }
                         }
                     }
                 }
             }
             )
async def profile_create_api_view(
    attrs: ProfileCreateShema,
    user: User = Depends(active_user),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    created_profile = await get_profile_by_id(
        user_id=user.id,
        session=session,
    )
    if created_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.PROFILE_IS_ALREADY_EXISTS,
        )
    profile = await crud.create_profile(
        attrs=attrs,
        user_id=user.id,
        session=session,
        )
    return profile


@router.get('/profile',
            name='users:profile_current_user',
            dependencies=[Depends(active_user)],
            response_model=ProfileRead,
            responses={
                status.HTTP_401_UNAUTHORIZED: {
                    "description": "Missing token or inactive user.",
                 },
            },
            )
async def get_profile_api_view(
    user: User = Depends(active_user),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await get_profile_by_id(
        user_id=user.id,
        session=session,
        )

router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))
