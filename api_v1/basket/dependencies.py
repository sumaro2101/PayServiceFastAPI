from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.permissions import active_user
from .dao import BasketDAO
from config.models import User, Basket
from config.database import db_connection


async def get_or_create_basket(
    user: User = Depends(active_user),
    session: AsyncSession = Depends(db_connection.session_geter),
) -> Basket:
    """
    Получение или создание корзины пользователя
    """
    basket_out = await BasketDAO.find_item_by_args(
        session=session,
        one_to_many=(Basket.coupon,),
        many_to_many=(Basket.products,),
        user_id=user.id,
    )
    if not basket_out:
        basket = await BasketDAO.add(
            session=session,
            user_id=user.id,
        )
        basket_out = await BasketDAO.find_item_by_args(
            session=session,
            many_to_many=(Basket.products,),
            id=basket.id,
        )
    return basket_out
