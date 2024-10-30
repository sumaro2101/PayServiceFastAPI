from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, and_
from sqlalchemy.orm import joinedload

from fastapi import HTTPException, status

from loguru import logger
from config.models import User, Basket, Order


async def get_basket(user: User,
                     unique_code: str,
                     session: AsyncSession,
                     ) -> Basket:
    stmt = (Select(Basket)
            .where(and_(Basket.user_id == user.id,
                        Basket.unique_temporary_id == unique_code))
            .options(joinedload(Basket.products)))
    basket: Basket = await session.scalar(statement=stmt)
    return basket


async def create_order(user: User,
                       session: AsyncSession,
                       ) -> Order:
    order_values = dict(user_id=user.id)
    order_model = Order(**order_values)
    session.add(order_model)
    await session.commit()
    await session.refresh(order_model)
    stmt = (Select(Order)
            .where(Order.id == order_model.id)
            .options(joinedload(Order.products)))
    order: Order = await session.scalar(statement=stmt)
    return order


async def switch_products_to_order(basket: Basket,
                                   order: Order,
                                   session: AsyncSession,
                                   ) -> Order:
    order.products.extend(basket.products)
    basket.products.clear()
    basket.unique_temporary_id = None
    await session.commit()
    return order


@logger.catch(reraise=True)
async def success_payment(user: User,
                          unique_code: str,
                          session: AsyncSession,
                          ) -> dict[str, str, Order]:
    if not unique_code:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                    detail=dict(order='Permission Denied'),
                    )
    basket = await get_basket(user=user,
                              unique_code=unique_code,
                              session=session,
                              )
    logger.info(f'get_basket = {basket}')
    if not basket:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=dict(order='Permission Denied'),
                            )
    if not basket.products:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=dict(basket='Basket is empty'),
                            )
    order = await create_order(user=user,
                               session=session,
                               )
    fill_order = await switch_products_to_order(
        basket=basket,
        order=order,
        session=session,
    )
    logger.info(f'unique code after = {basket.unique_temporary_id}')
    out = dict(state='success',
               detail='Your order is create',
               order=fill_order,
               )
    return out


async def cancel_payment(user: User,
                         unique_code: str,
                         session: AsyncSession,
                         ) -> dict[str, str]:
    if not unique_code:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                    detail=dict(order='Permission Denied'),
                    )
    basket = await get_basket(user=user,
                              unique_code=unique_code,
                              session=session,
                              )
    if not basket:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=dict(order='Permission Denied'),
                            )

    basket.unique_temporary_id = None
    await session.commit()
    return dict(state='success',
                detail='Order is cancel',
                )
