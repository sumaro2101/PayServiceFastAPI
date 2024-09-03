from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from sqlalchemy.orm import joinedload

from config.models import Post, User
from .schemas import PostCreateSchema


async def get_post(post_id: int,
                   session: AsyncSession) -> Post:
    stmt = Select(Post).where(Post.id == post_id).options(joinedload(Post.user).joinedload(User.profile))
    return await session.scalar(stmt)


async def get_list_posts(session: AsyncSession) -> list[Post]:
    stmt = Select(Post).options(joinedload(Post.user)).order_by(Post.id)
    posts = await session.scalars(stmt)
    return list(posts)


async def create_post(attrs: PostCreateSchema,
                      user: int,
                      session: AsyncSession,
                      ) -> Post:
    post = Post(user_id=user,
                **attrs.model_dump(),
                )
    session.add(post)
    await session.commit()
    return post
