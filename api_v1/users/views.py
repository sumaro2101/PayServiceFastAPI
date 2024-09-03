from typing import Annotated
from fastapi import APIRouter, Depends, status, Path

from sqlalchemy.ext.asyncio import AsyncSession

from config.models import User, db_helper, Profile
from .schemas import (UserCreateSchema,
                      UserUpdateSchema,
                      ProfileCreateShema,
                      )
from . import crud
from .dependencies import get_user_by_id, get_profile_by_id


router = APIRouter(prefix='/users',
                   tags=['users'],
                   )


@router.get('/{user_id}/',
            name='Получение пользователя',
            )
async def get_user_api_view(user: User = Depends(get_user_by_id)):
    """Получение пользователя
    """
    return user


@router.get('/',
            name='Список пользователей',
            )
async def get_list_user_api_view(session: AsyncSession = Depends(db_helper.session_geter)):
    return await crud.get_list_users(session=session)


@router.post('/create/',
             status_code=status.HTTP_201_CREATED,
             name='Создание пользователя',
             )
async def create_user(user: UserCreateSchema,
                      session: AsyncSession = Depends(db_helper.session_geter),
                      ):
    """Создание пользователя
    """
    return await crud.create_user(user, session)


@router.patch('/update/{user_id}/',
              name='Обновление пользователя',
              )
async def update_user(attrs: UserUpdateSchema,
                      user: User = Depends(get_user_by_id),
                      session: AsyncSession = Depends(db_helper.session_geter)):
    """Обновление пользователя
    """
    return await crud.update_user(user=user,
                                  attrs=attrs,
                                  session=session)


@router.delete('/delete/{user_id}/',
               name='Удаление пользователя',
               status_code=status.HTTP_204_NO_CONTENT,
               responses=None,
               )
async def delete_user(user: User = Depends(get_user_by_id),
                      session: AsyncSession = Depends(db_helper.session_geter),
                      ):
    """Удаление пользователя
    """
    await crud.delete_user(user=user,
                     session=session,
                     )


# profile
@router.post('/profile/create/{user_id}/',
             name='Создание профиля для пользователя',
             status_code=status.HTTP_201_CREATED,
             )
async def profile_create_api_view(attrs: ProfileCreateShema,
                                  user_id: Annotated[int,
                                                     Path(ge=1),
                                                     ],
                                  session: AsyncSession = Depends(db_helper.session_geter),
                                  ):
    profile = await crud.create_profile(attrs=attrs,
                                        user=user_id,
                                        session=session)
    return profile


@router.get('/profile/{profile_id}/',
            name='Получение профиля',
            )
async def get_profile_api_view(profile: Profile = Depends(get_profile_by_id)):
    return profile
