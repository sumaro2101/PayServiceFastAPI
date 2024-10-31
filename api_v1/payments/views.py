from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.models import User, db_helper
from api_v1.auth.auth_validators import get_user_by_hash
from . import crud


router = APIRouter(prefix='/payments',
                   tags=['Payments'],
                   )


@router.get(path='/success/{uid}/{token}/{unique_code}/')
async def success_payment(unique_code: str,
                          user: User = Depends(get_user_by_hash),
                          session: AsyncSession = Depends(db_helper.session_geter),
                          ):
    session_payment = crud.PaymentManager(
        user=user,
        unique_code=unique_code,
        session=session
    )
    order = await session_payment.get_order()
    return order


@router.get(path='/cancel/{uid}/{token}/{unique_code}/',
            status_code=status.HTTP_204_NO_CONTENT,
            )
async def get_cancel(unique_code: str,
                     user: User = Depends(get_user_by_hash),
                     session: AsyncSession = Depends(db_helper.session_geter),
                     ):
    session_payment = crud.PaymentManager(
        user=user,
        unique_code=unique_code,
        session=session
    )
    await session_payment.cancel_payment()
