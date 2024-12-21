from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from loguru import logger

from api_stripe.abs import Stripe
from config.models.user import User
from .schemas import CouponSchemaCreate, CouponSchemaUpdate
from .dao import PromoDAO
from config.models import Coupon
from api_v1.users.dao import UserDAO
from api_v1.promos.tasks import (
    update_coupon_stripe_task,
    delete_coupon_stripe_task,
    )


async def get_list_promos(session: AsyncSession) -> list[Coupon]:
    return await PromoDAO.find_all_items_by_args(
        session=session,
        one_to_many=(Coupon.users,),
    )


async def create_coupon(coupon_schema: CouponSchemaCreate,
                        stripe_action: Stripe,
                        session: AsyncSession,
                        ) -> Coupon:
    created_coupon = await PromoDAO.find_item_by_args(
        session=session,
        number=coupon_schema.number,
    )
    if created_coupon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Coupon is already exists',
            )
    logger.info(f'time end_at = {coupon_schema.end_at}')
    coupon_schema.end_at = coupon_schema.end_at.replace(tzinfo=None)
    coupon = await PromoDAO.add(
        session=session,
        **coupon_schema.model_dump()
    )
    stripe = stripe_action(target=coupon.__dict__)
    await stripe.action()
    return coupon


async def update_coupon(coupon_schema: CouponSchemaUpdate,
                        coupon: Coupon,
                        session: AsyncSession,
                        ) -> Coupon:
    update_schema = coupon_schema.model_dump(exclude_unset=True)
    if not update_schema:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=dict(coupon='Body mast have no less one field'),
            )
    coupon = await PromoDAO.update(
        session=session,
        instance=coupon,
        **update_schema,
    )
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
                        session: AsyncSession,
                        ) -> None:
    stripe_value = dict(id=coupon.id)
    await PromoDAO.delete(session=session, instance=coupon)
    delete_coupon_stripe_task.delay(stripe_value)


async def gift_to_user(user_id: int,
                       coupon: Coupon,
                       session: AsyncSession,
                       ) -> Coupon:
    if not coupon.active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=dict(coupon='Coupon is not active'),
                            )
    user = await UserDAO.find_item_by_args(
        session=session,
        many_to_many=(User.coupons,),
        id=user_id,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found',
        )
    if coupon in user.coupons:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=dict(coupon='This coupon is already have user'),
            )
    user.coupons.append(coupon)
    await session.commit()
    return coupon


async def gift_to_all_active_users(coupon: Coupon,
                                   session: AsyncSession,
                                   ):
    users: list[User] = await UserDAO.find_all_items_by_args(
        session=session,
        many_to_many=(User.coupons,),
        is_active=True,
    )
    count_add_users = 0
    for user in users:
        if coupon not in user.coupons:
            user.coupons.append(coupon)
            count_add_users += 1
    if count_add_users:
        await session.commit()
    out = coupon.__dict__ | {'users_count_added': count_add_users}
    return out


async def remove_all_coupons_from_users(coupon: Coupon,
                                        session: AsyncSession,
                                        ):
    users: list[User] = await UserDAO.find_all_items_by_args(
        session=session,
        many_to_many=(User.coupons,),
        is_active=True,
    )
    count_remove_users = 0
    for user in users:
        if coupon in user.coupons:
            user.coupons.remove(coupon)
            count_remove_users += 1
    if count_remove_users:
        await session.commit()
    out = coupon.__dict__ | {'users_count_added': count_remove_users}
    return out


async def remove_from_user(user_id: int,
                           coupon: Coupon,
                           session: AsyncSession,
                           ) -> Coupon:
    user = await UserDAO.find_item_by_args(
        session=session,
        many_to_many=(User.coupons,),
        id=user_id,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found',
        )
    try:
        user.coupons.remove(coupon)
        await session.commit()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=dict(coupon='This coupon is not prezent to user'),
            )
    return coupon
