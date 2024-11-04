from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, ScalarResult
from sqlalchemy.orm import selectinload, joinedload

from fastapi import HTTPException, status

from config.models import Order
from .schemas import OrderCreateSchema, OrderUpdateSchema
from .utils import get_list_orders_to_append


async def get_order(order_id: int,
                    session: AsyncSession,
                    ):
    stmt = (Select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.products),
                     joinedload(Order.coupon)))
    result: ScalarResult = await session.scalar(stmt)
    return result


async def create_order(session: AsyncSession,
                       order_schema: OrderCreateSchema,
                       ) -> Order:
    order = Order(**order_schema.model_dump(exclude='products'))
    session.add(order)
    await session.commit()
    await session.refresh(order)
    stmt = (Select(Order).
                      where(Order.id == order.id).
                      options(selectinload(Order.products)))
    new_order = await session.scalar(stmt)
    products = await get_list_orders_to_append(session, order_schema.products)
    new_order.products += products
    await session.commit()
    return order


async def update_order(session: AsyncSession,
                       order: Order,
                       attrs: OrderUpdateSchema,
                       ):
    attrs = attrs.model_dump(exclude_unset=True,)
    ids_product = False
    if 'products' in attrs:
        ids_product = attrs['products']
        if ids_product == []:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Нельзя указывать заказ без продуктов',
                                )
        else:
            products = await get_list_orders_to_append(session=session,
                                                       ids_product=ids_product,
                                                       )
        del attrs['products']

    for key, value in attrs.items():
        setattr(order, key, value)
    order.products = products
    await session.commit()
    return order


async def list_orders(session: AsyncSession):
    stmt = (Select(Order)
            .order_by(Order.id)
            .options(selectinload(Order.products),
                     joinedload(Order.coupon)))
    result: ScalarResult = list(await session.scalars(stmt))
    return result
