from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.models import User
from config.database import db_connection
from api_v1.users.dependencies import get_user_by_hash
from . import crud
from .schemas import ReadSuccessPayment


router = APIRouter(prefix='/payments',
                   tags=['Payments'],
                   )


@router.get(path='/success/{uid}/{token}/{unique_code}',
            name='payments:success',
            response_model=ReadSuccessPayment,
            responses={
                status.HTTP_403_FORBIDDEN: {
                    'description': 'Hash is wrong or unique code or basket empty.',
                },
                status.HTTP_400_BAD_REQUEST: {
                    'description': 'Stripe expire session error.',
                }
            }
            )
async def success_payment(
    unique_code: str,
    user: User = Depends(get_user_by_hash),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    session_payment = crud.PaymentManager(
        user=user,
        unique_code=unique_code,
        session=session
    )
    order = await session_payment.get_order()
    return order


@router.get(path='/cancel/{uid}/{token}/{unique_code}',
            status_code=status.HTTP_204_NO_CONTENT,
            )
async def get_cancel(
    unique_code: str,
    user: User = Depends(get_user_by_hash),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    session_payment = crud.PaymentManager(
        user=user,
        unique_code=unique_code,
        session=session
    )
    await session_payment.cancel_payment()
