from fastapi import APIRouter, Depends, status, Path

from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.users.dependencies import get_user_by_id
from .schemas import PostCreateSchema
from .dependencies import get_post_by_id
from . import crud
from config.models import User, Post, db_helper


router = APIRouter(tags=['Posts'],
                   prefix='/posts',
                   )


@router.get('/{post_id}/',
            name='Получение поста',
            )
async def get_post_api_view(post: Post = Depends(get_post_by_id)):
    return post


@router.get('/',
            name='Список постов',
            )
async def get_list_posts_api_view(session: AsyncSession = Depends(db_helper.session_geter)):
    return await crud.get_list_posts(session=session)


@router.post('/{user_id}/',
             name='Создание поста',
             status_code=status.HTTP_201_CREATED,
             )
async def create_post_api_view(attrs: PostCreateSchema,
                               user_id: Annotated[int,
                                                  Path(gt=1),
                                                  ],
                               session: AsyncSession = Depends(db_helper.session_geter),
                               ):
    return await crud.create_post(attrs=attrs,
                            user=user_id,
                            session=session)
