from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends

from .dao import PromoDAO
from .common import ErrorCode
from config.models import Coupon
from config.database import db_connection


async def get_coupon_by_name(
    coupon_name: str,
    session: AsyncSession = Depends(db_connection.session_geter),
) -> Coupon:
    coupon = await PromoDAO.find_item_by_args(
        session=session,
        number=coupon_name,
    )
    if not coupon:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.COUPON_NOT_FOUND,
                )
    return coupon


async def get_full_coupone(
    coupon_name: str,
    session: AsyncSession = Depends(db_connection.session_geter),
) -> Coupon:
    coupon = await PromoDAO.find_item_by_args(
        session=session,
        number=coupon_name,
        many_to_many=(Coupon.users,),
    )
    if not coupon:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.COUPON_NOT_FOUND,
                )
    return coupon
