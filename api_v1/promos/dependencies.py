from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from sqlalchemy.orm import selectinload

from fastapi import HTTPException, status, Depends

from config.models import Coupon, db_helper
from config.models.user import User


async def get_coupon_by_name(coupon_name: str,
                             session: AsyncSession = Depends(db_helper.session_geter),
                             ) -> Coupon:
    stmt = (Select(Coupon)
            .where(Coupon.number == coupon_name)
            .options(selectinload(Coupon.users)))
    coupon = await session.scalar(statement=stmt)
    if not coupon:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=dict(coupon=f'Coupon {coupon_name} is not found'),
                            )
    return coupon
