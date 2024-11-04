from fastapi import Depends
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from api_v1.auth.auth_validators import get_current_active_user
from api_v1.basket.schemas import BaseBasketSchema
from config.models import User, Basket, db_helper


async def get_or_create_basket(
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.session_geter),
    ) -> Basket:
    """
    Получение или создание корзины пользователя
    """
    stmt = (Select(Basket)
            .where(Basket.user_id == user.id)
            .options(joinedload(Basket.products),
                     selectinload(Basket.coupon)))
    basket = await session.scalar(statement=stmt)
    if not basket:
        schema = BaseBasketSchema(user_id=user.id)
        basket = Basket(**schema.model_dump(exclude='products'))
        session.add(basket)
        await session.commit()
        await session.refresh(basket)
        stmt = (Select(Basket)
            .where(Basket.user_id == user.id)
            .options(joinedload(Basket.products)))
        basket = await session.scalar(statement=stmt)
    # basket_out = BasketView(**basket.__dict__)
    return basket
