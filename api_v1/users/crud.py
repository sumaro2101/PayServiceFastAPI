from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from sqlalchemy.orm import joinedload

from .schemas import ProfileCreateShema
from config.models import User, Profile


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
