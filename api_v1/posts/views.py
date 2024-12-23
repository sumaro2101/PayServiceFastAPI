from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import PostCreateSchema
from .dependencies import get_post_by_id
from . import crud
from api_v1.auth.permissions import active_user
from config.models import Post, User
from config.database import db_connection


router = APIRouter(tags=['Posts'],
                   prefix='/posts',
                   )


@router.get('/{post_id}',
            name='Получение поста',
            )
async def get_post_api_view(post: Post = Depends(get_post_by_id)):
    return post


@router.get('',
            name='Список постов',
            )
async def get_list_posts_api_view(
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.get_list_posts(session=session)


@router.post('/{user_id}',
             name='Создание поста',
             status_code=status.HTTP_201_CREATED,
             )
async def create_post_api_view(
    attrs: PostCreateSchema,
    active_user: User = Depends(active_user),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.create_post(
        attrs=attrs,
        user=active_user.id,
        session=session,
        )
