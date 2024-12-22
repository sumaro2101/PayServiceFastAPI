from sqlalchemy.ext.asyncio import AsyncSession

from config.models import Post
from .schemas import PostCreateSchema
from .dao import PostDAO


async def get_post(post_id: int,
                   session: AsyncSession) -> Post:
    return await PostDAO.find_item_by_args(
        session=session,
        one_to_many=(Post.user,),
        id=post_id,
    )


async def get_list_posts(session: AsyncSession) -> list[Post]:
    return await PostDAO.find_all_items_by_args(
        session=session,
        one_to_many=(Post.user,),
        order_by=(Post.id,),
    )


async def create_post(attrs: PostCreateSchema,
                      user: int,
                      session: AsyncSession,
                      ) -> Post:
    post = await PostDAO.add(
        session=session,
        user_id=user,
        **attrs.model_dump(),
    )
    return post
