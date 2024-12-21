from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from sqlalchemy.orm import joinedload, selectinload

from .schemas import ProfileCreateShema
from config.models import User, Profile
from loguru import logger


@logger.catch(reraise=True)
async def get_list_users(session: AsyncSession) -> list[User]:
    """Вывод всех пользователей
    """
    stmt = (Select(User).
            options(joinedload(User.profile),
                    selectinload(User.coupons),
                    selectinload(User.posts)).
            order_by(User.id))
    users = await session.scalars(stmt)
    return list(users.unique())


@logger.catch(reraise=True)
async def get_active_list_users(session: AsyncSession) -> list[User]:
    """Вывод всех активных пользователей
    """
    stmt = (Select(User)
            .where(User.active == True)
            .options(selectinload(User.coupons)))
    users = await session.scalars(stmt)
    return list(users.unique())


async def create_profile(attrs: ProfileCreateShema,
                         user_id: int,
                         session: AsyncSession,
                         ):
    """Механиз создания профиля
    """
    profile = Profile(user_id=user_id,
                      **attrs.model_dump(),
                      )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


async def get_profile(user_id: int,
                      session: AsyncSession,
                      ) -> Profile:
    """Получения профиля
    """
    stmt = (Select(Profile).
            where(Profile.user_id == user_id).
            options(joinedload(Profile.user).selectinload(User.posts)))
    profile = await session.scalar(stmt)
    return profile
