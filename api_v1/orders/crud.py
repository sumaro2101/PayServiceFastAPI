from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status

from config.models import Order
from .schemas import OrderCreateSchema, OrderUpdateSchema
from .utils import get_list_orders_to_append
from .dao import OrderDAO
from api_v1.promos.dao import PromoDAO


async def get_order_by_user_and_coupone(
    user_id: int,
    coupon_id: int,
    session: AsyncSession,
) -> Order | None:
    return await OrderDAO.find_item_by_args(
        session=session,
        user_id=user_id,
        coupon_id=coupon_id,
    )


async def get_order(order_id: int,
                    session: AsyncSession,
                    ):
    return await OrderDAO.find_item_by_args(
        session=session,
        id=order_id,
        one_to_many=(Order.coupon,),
        many_to_many=(Order.products,),
    )


async def create_order(session: AsyncSession,
                       user_id: int,
                       order_schema: OrderCreateSchema,
                       ) -> Order:
    coupon_id = None
    if order_schema.promocode:
        coupon = await PromoDAO.find_item_by_args(
            session=session,
            number=order_schema.promocode,
        )
        coupon_id = coupon.id
    order = await OrderDAO.add(
        session=session,
        coupon_id=coupon_id,
        user_id=user_id,
        **order_schema.model_dump(exclude='products, promocode'),
    )
    new_order = await OrderDAO.find_item_by_args(
        session=session,
        id=order.id,
        many_to_many=(Order.products,),
    )
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
            products = await get_list_orders_to_append(
                session=session,
                ids_product=ids_product,
                )
        del attrs['products']
    for key, value in attrs.items():
        setattr(order, key, value)
    order.products = products
    await session.commit()
    return order


async def delete_order(
    session: AsyncSession,
    order: Order,
) -> None:
    await OrderDAO.delete(
        session=session,
        instance=order,
    )


async def list_orders(session: AsyncSession):
    return await OrderDAO.find_all_items_by_args(
        session=session,
        one_to_many=(Order.coupon,),
        many_to_many=(Order.products,),
        order_by=(Order.id,),
    )
