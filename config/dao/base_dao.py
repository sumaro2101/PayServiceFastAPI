from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Select
from sqlalchemy.orm import joinedload, selectinload
from typing import ClassVar, Sequence

from config.models import Base


class BaseDAO:
    """
    Базовый DAO класс для CRUD модели

    Универсальный класс для легкого опеределения

    CRUD модели

    Примеры::

        # Поиск сущности
        item = ModelDAO.find_item_by_args(
            session=session,
            id=3,
        )
        # Множественный поиск сущностей
        items = ModelDAO.find_all_items_by_args(
            session = session,
            one_to_many = (Model.tag,),
            many_to_many = (Model.users, Model.stations,)
            order_by = (Model.id,)
            name='model',
        )
        # Создание сущности
        item = ModelDAO.add(
            session,
            id=3,
            name='model',
            )
    """
    model: ClassVar[Base | None] = None

    @classmethod
    async def find_item_by_args(cls,
                                session: AsyncSession,
                                one_to_many: Sequence[Base] | None = None,
                                many_to_many: Sequence[Base] | None = None,
                                order_by: Sequence[Base] | None = None,
                                **kwargs: dict[str, str | int],
                                ) -> Base | None:
        """
        Нахождение и возращение сущности

        Args:
            session (AsyncSession): Текущая сессия

            one_to_many (Sequence[BaseModel] | None, optional): Выбранные поля
                для one_to_many
                которые имеют отношение например: (Product.user)

            many_to_many (Sequence[BaseModel] | None, optional): Выбранные поля
                для many_to_many
                которые имеют отношение например: (Product.categories)

        Returns:
            BaseModel: Сущность из выборки
        """
        stmt = struct_options_statment(
            model=cls.model,
            one_to_many=one_to_many,
            many_to_many=many_to_many,
            order_by=order_by,
            **kwargs,
        )
        result = await session.scalar(statement=stmt)
        return result

    @classmethod
    async def find_all_items_by_args(cls,
                                     session: AsyncSession,
                                     one_to_many: Sequence[Base] | None = None,
                                     many_to_many: Sequence[Base] | None = None,
                                     order_by: Sequence[Base] | None = None,
                                     **kwargs: dict[str, str | int],
                                     ) -> list[Base] | None:
        """
        Нахождение и возращение множества сущностей

        Args:
            session (AsyncSession): Текущая сессия

            one_to_many (Sequence[BaseModel] | None, optional): Выбранные поля
                для one_to_many
                которые имеют отношение например: (Product.user)

            many_to_many (Sequence[BaseModel] | None, optional): Выбранные поля
                для many_to_many
                которые имеют отношение например: (Product.categories)

        Returns:
            BaseModel: Сущности из выборки
        """
        stmt = struct_options_statment(
            model=cls.model,
            one_to_many=one_to_many,
            many_to_many=many_to_many,
            order_by=order_by,
            **kwargs,
        )
        result = await session.scalars(statement=stmt)
        return list(result.unique())

    @classmethod
    async def add(cls,
                  session: AsyncSession,
                  **values,
                  ) -> Base:
        instance = cls.model(**values)
        session.add(instance=instance)
        try:
            await session.commit()
        except SQLAlchemyError as ex:
            await session.rollback()
            raise ex
        return instance

    @classmethod
    async def update(cls,
                     session: AsyncSession,
                     instance: Base,
                     **values,
                     ) -> Base:
        [setattr(instance, name, value)
         for name, value
         in values.items()]
        await session.commit()
        return instance

    @classmethod
    async def delete(cls,
                     session: AsyncSession,
                     instance: Base,
                     ) -> None:
        await session.delete(instance)
        await session.commit()


def struct_options_statment(model: Base,
                            one_to_many: Sequence[Base] | None = None,
                            many_to_many: Sequence[Base] | None = None,
                            order_by: Sequence[Base] | None = None,
                            **kwargs: dict[str, str | int],
                            ) -> Select:
    """
    Струкрутирование запроса SELECT для выборки

    Args:
        model (BaseModel): Модель таблицы для выборки
        one_to_many (Sequence[BaseModel] | None, optional): Выбранные поля
            для one_to_many
            которые имеют отношение например: (Product.user)

        many_to_many (Sequence[BaseModel] | None, optional): Выбранные поля
            для many_to_many
            которые имеют отношение например: (Product.categories)

    Returns:
        Select: Экземпляр запроса
    """

    stms_one_to_many = ([selectinload(join) for join in list(one_to_many)]
                        if one_to_many
                        else list())
    stmt_any_to_many = ([joinedload(join) for join in list(many_to_many)]
                        if many_to_many
                        else list())
    stmt_order_by = list(order_by) if order_by else list()
    stmt = (Select(model)
            .filter_by(**kwargs)
            .options(*stms_one_to_many)
            .options(*stmt_any_to_many)
            .order_by(*stmt_order_by))
    return stmt
