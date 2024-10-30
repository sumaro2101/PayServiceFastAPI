from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, Result
from sqlalchemy.orm import joinedload, selectinload

from .schemas import UserCreateSchema, UserUpdateSchema, ProfileCreateShema
from config.models import User, Profile
from .utils import PasswordsHandler
from loguru import logger


# for dependencies
async def get_user(user_id: int,
                   session: AsyncSession,
                   ) -> User:
    """Механизм получения пользователя
    """
    stmt = (Select(User).
            where(User.id == user_id).
            options(joinedload(User.profile),
                    selectinload(User.posts),
                    selectinload(User.coupons),
                    ))
    user = await session.scalar(stmt)
    return user


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


async def create_user(user_create: UserCreateSchema,
                      session: AsyncSession,
                      ) -> User:
    """Механизм создания пользователя
    """
    hashed_password = PasswordsHandler(password1=user_create.password1,
                                       password2=user_create.password2,
                                       ).get_hash_password()
    user = User(**UserCreateSchema.model_dump(user_create, exclude=('password1', 'password2')),
                password=hashed_password,
                )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(user: User,
                      attrs: UserUpdateSchema,
                      session: AsyncSession,
                      ) -> User:
    """Механизм обновления пользователя
    """
    for name, value in attrs.model_dump(exclude_unset=True).items():
        setattr(user, name, value)
    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(user: User,
                      session: AsyncSession,
                      ) -> None:
    """Механизм удаления пользователя
    """
    await session.delete(user)
    await session.commit()


async def create_profile(attrs: ProfileCreateShema,
                         user_id: int,
                         session: AsyncSession,
                         ):
    """Механиз создания профиля
    """
    profile = Profile(user_id=user_id,
                      **attrs.model_dump(),
                      )
    await session.commit()
    return profile


async def get_profile(profile_id: int,
                      session: AsyncSession,
                      ) -> Profile:
    """Получения профиля
    """
    stmt = (Select(Profile).
            where(Profile.id == profile_id).
            options(joinedload(Profile.user).selectinload(User.posts)))
    profile = await session.scalar(stmt)
    return profile
