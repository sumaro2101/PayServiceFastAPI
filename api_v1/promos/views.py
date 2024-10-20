from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, status, Depends

from .schemas import (CouponViewSchema,
                      CouponSchema,
                      CouponSchemaCreate,
                      CouponSchemaUpdate,
                      ActivityCouponeSchema,
                      )
from . import crud
from .dependencies import get_coupon_by_name
from config.models import db_helper, Coupon


router = APIRouter(prefix='/coupons',
                   tags=['Coupons'],
                   )


@router.put(path='/create/',
            description='Создания купона',
            response_model=CouponSchema,
            status_code=status.HTTP_201_CREATED,
            )
async def create_coupone(coupon_schema: CouponSchemaCreate,
                         session: AsyncSession = Depends(db_helper.session_geter)):
    return await crud.create_coupon(
        coupon_schema=coupon_schema,
        session=session,
    )


@router.get(path='/list/',
            description='Получение списка купонов',
            response_model=list[CouponViewSchema])
async def get_list_promos(session: AsyncSession = Depends(db_helper.session_geter)):
    return await crud.get_list_promos(session=session)


@router.patch(path='/update/{coupon_name}/',
              description='Обновление купона',
              response_model=CouponSchema,
              )
async def update_coupon(coupon_schema: CouponSchemaUpdate,
                         coupon: Coupon = Depends(get_coupon_by_name),
                         session: AsyncSession = Depends(db_helper.session_geter),
                         ):
    return await crud.update_coupon(
        coupon_schema=coupon_schema,
        coupon=coupon,
        session=session,
    )

@router.get(path='/get/{coupon_name}/',
            description='Получение купона',
            response_model=CouponViewSchema,
            )
async def get_coupon(coupon: Coupon = Depends(get_coupon_by_name)):
    return coupon


@router.patch(path='/activate/{coupon_name}/',
              description='Активация купона по имени',
              response_model=ActivityCouponeSchema,
              )
async def activate_coupon(coupon: Coupon = Depends(get_coupon_by_name),
                          session: AsyncSession = Depends(db_helper.session_geter),
                          ):
    return await crud.activate_coupon(
        coupon=coupon,
        session=session,
    )


@router.patch(path='/deactivate/{coupon_name}/',
              description='Деактивация купона',
              response_model=ActivityCouponeSchema,
              )
async def deactivate_coupon(coupon: Coupon = Depends(get_coupon_by_name),
                            session: AsyncSession = Depends(db_helper.session_geter),
                            ):
    return await crud.deactivate_coupon(
        coupon=coupon,
        session=session,
    )
