from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from sqlalchemy.orm import joinedload

from fastapi import status, HTTPException

from .schemas import CouponSchemaCreate, CouponSchemaUpdate
from config.models import Coupon


async def get_list_promos(session: AsyncSession):
    stmt = (Select(Coupon)
            .options(joinedload(Coupon.users))
            .order_by(Coupon.active))
    coupons = await session.scalars(statement=stmt)
    return list(coupons)


async def create_coupon(coupon_schema: CouponSchemaCreate,
                        session: AsyncSession,
                        ) -> Coupon:
    coupon = Coupon(**coupon_schema.model_dump())
    session.add(coupon)
    await session.commit()
    await session.refresh(coupon)
    return coupon


async def update_coupon(coupon_schema: CouponSchemaUpdate,
                         coupon: Coupon,
                         session: AsyncSession,
                         ) -> Coupon:
    update_schema = coupon_schema.model_dump(exclude_unset=True)
    [setattr(coupon, name, value)
     for name, value
     in update_schema.items()]
    await session.commit()
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
