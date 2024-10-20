from fastapi import APIRouter, Depends
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
    return await crud.success_payment(user=user,
                                      unique_code=unique_code,
                                      session=session,
                                      )


@router.get(path='/cancel/')
async def get_cancel():
    return dict(payment='payment has cancel')
