from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from sqlalchemy.orm import selectinload

from fastapi import status, HTTPException

from loguru import logger

from stripe import _error

from api_stripe.abs import Stripe
from config.models.user import User

from .schemas import CouponSchemaCreate, CouponSchemaUpdate
from config.models import Coupon
from api_stripe.handler import error_stripe_handle
from api_v1.users.crud import get_active_list_users, get_list_users
from api_v1.promos.tasks import (
    update_coupon_stripe_task,
    delete_coupon_stripe_task,
    )


async def get_list_promos(session: AsyncSession) -> list[Coupon]:
    stmt = (Select(Coupon)
            .options(selectinload(Coupon.users))
            .order_by(Coupon.active))
    promos = await session.scalars(stmt)
    return list(promos)


async def create_coupon(coupon_schema: CouponSchemaCreate,
                        stripe_action: Stripe,
                        session: AsyncSession,
                        ) -> Coupon:
    logger.info(f'time end_at = {coupon_schema.end_at}')
    coupon_schema.end_at = coupon_schema.end_at.replace(tzinfo=None)
    coupon = Coupon(**coupon_schema.model_dump())
    session.add(coupon)
    await session.commit()
    await session.refresh(coupon)
    try:
        stripe = stripe_action(target=coupon.__dict__)
        await stripe.action()
    except _error.InvalidRequestError as ex:
        await session.delete(coupon)
        await session.commit()
        msg = error_stripe_handle(err=ex)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=dict(stripe=msg))
    return coupon


async def update_coupon(coupon_schema: CouponSchemaUpdate,
                        stripe_action: Stripe,
                        coupon: Coupon,
                        session: AsyncSession,
                        ) -> Coupon:
    update_schema = coupon_schema.model_dump(exclude_unset=True)
    if not update_schema:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=dict(coupon='Body mast have no less one field'),
                            )
    [setattr(coupon, name, value)
     for name, value
     in update_schema.items()]
    await session.commit()
    update_schema.update(id=coupon.id)
    update_coupon_stripe_task.delay(update_schema)
    return coupon


async def activate_coupon(coupon: Coupon,
                          session: AsyncSession,
                          ) -> Coupon:
    if coupon.active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=dict(coupon='Coupon is already active'),
                            )
    coupon.active = True
    await session.commit()
    return coupon


async def deactivate_coupon(coupon: Coupon,
                            session: AsyncSession,
                            ) -> Coupon:
    if not coupon.active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=dict(coupon='Coupon is already non active'),
                            )
    coupon.active = False
    await session.commit()
    return coupon


async def delete_coupon(coupon: Coupon,
                        stripe_action: Stripe,
                        session: AsyncSession,
                        ) -> None:
    stripe_value = dict(id=coupon.id)
    await session.delete(coupon)
    await session.commit()
    delete_coupon_stripe_task.delay(stripe_value)


async def gift_to_user(user: User,
                       coupon: Coupon,
                       session: AsyncSession,
                       ) -> Coupon:
    if not coupon.active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=dict(coupon='Coupon is not active'),
                            )
    if coupon in user.coupons:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail=dict(coupon='This coupon is already have user'),
                        )
    user.coupons.append(coupon)
    await session.commit()
    return coupon


async def gift_to_all_active_users(coupon: Coupon,
                                   session: AsyncSession,
                                   ):
    users: list[User] = await get_active_list_users(session=session)
    count_add_users = 0
    for user in users:
        if coupon not in user.coupons:
            user.coupons.append(coupon)
            count_add_users += 1
    if count_add_users:
        await session.commit()
    out = coupon.__dict__ | {'users_count': count_add_users}
    return out


async def remove_all_coupons_from_users(coupon: Coupon,
                                        session: AsyncSession,
                                        ):
    users: list[User] = await get_list_users(session=session)
    count_remove_users = 0
    for user in users:
        if coupon in user.coupons:
            user.coupons.remove(coupon)
            count_remove_users += 1
    if count_remove_users:
        await session.commit()
    out = coupon.__dict__ | {'users_count': count_remove_users}
    return out


async def remove_from_user(user: User,
                           coupon: Coupon,
                           session: AsyncSession,
                           ) -> Coupon:
    try:
        user.coupons.remove(coupon)
        await session.commit()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=dict(coupon='This coupon is not prezent to user'),
                            )
    return coupon
