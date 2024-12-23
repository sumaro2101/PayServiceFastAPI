from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.permissions import superuser
from .schemas import OrderCreateSchema, OrderUpdateSchema
from . import crud
from config.database import db_connection
from config.models import Order, User
from .dependencies import get_order_by_id


router = APIRouter(prefix='/orders',
                   tags=['Orders'],
                   )


@router.post('/create',
             name='Создание заказа',
             status_code=status.HTTP_201_CREATED,
             )
async def create_order_api_view(
    order: OrderCreateSchema,
    user: User = Depends(superuser),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.create_order(
        order_schema=order,
        user_id=user.id,
        session=session,
        )


@router.patch('/{order_id}/update',
              name='Обновление заказа',
              )
async def update_order_api_view(
    attrs: OrderUpdateSchema,
    order: Order = Depends(get_order_by_id),
    user: User = Depends(superuser),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.update_order(session=session,
                                   order=order,
                                   attrs=attrs)


@router.get('',
            name='Список заказов',
            )
async def list_orders_api_view(
    session: AsyncSession = Depends(db_connection.session_geter),
    user: User = Depends(superuser),
):
    return await crud.list_orders(session=session)


@router.delete('/{order_id}/delete',
               name='Удаление заказа',
               status_code=status.HTTP_204_NO_CONTENT,
               )
async def delete_order_api_view(
    session: AsyncSession = Depends(db_connection.session_geter),
    order: Order = Depends(get_order_by_id),
    user: User = Depends(superuser),
):
    await crud.delete_order(
        session=session,
        order=order,
    )
