from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, status, Depends

from .schemas import (CouponViewSchema,
                      CouponSchema,
                      CouponSchemaCreate,
                      CouponSchemaUpdate,
                      ActivityCouponeSchema,
                      CouponAddCountUser,
                      )
from . import crud
from api_v1.auth.permissions import superuser
from .dependencies import get_coupon_by_name
from config.database import db_connection
from config.models import Coupon, User
from api_stripe.api import (CreateDiscountCoupon)


router = APIRouter(prefix='/coupons',
                   tags=['Coupons'],
                   )


@router.put(path='/create',
            description='Создания купона',
            response_model=CouponSchema,
            status_code=status.HTTP_201_CREATED,
            )
async def create_coupone(
    coupon_schema: CouponSchemaCreate,
    superuser: User = Depends(superuser),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.create_coupon(
        coupon_schema=coupon_schema,
        stripe_action=CreateDiscountCoupon,
        session=session,
    )


@router.get(path='/list',
            description='Получение списка купонов',
            response_model=list[CouponViewSchema],
            )
async def get_list_promos(
    session: AsyncSession = Depends(db_connection.session_geter),
    superuser: User = Depends(superuser),
):
    return await crud.get_list_promos(session=session)


@router.patch(path='/update/{coupon_name}',
              description='Обновление купона',
              response_model=CouponSchema,
              )
async def update_coupon(
    coupon_schema: CouponSchemaUpdate,
    superuser: User = Depends(superuser),
    coupon: Coupon = Depends(get_coupon_by_name),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.update_coupon(
        coupon_schema=coupon_schema,
        coupon=coupon,
        session=session,
    )


@router.get(path='/get/{coupon_name}',
            description='Получение купона',
            )
async def get_coupon(coupon: Coupon = Depends(get_coupon_by_name),
                     superuser: User = Depends(superuser),
                     ):
    return coupon


@router.patch(path='/activate/{coupon_name}',
              description='Активация купона по имени',
              response_model=ActivityCouponeSchema,
              )
async def activate_coupon(
    coupon: Coupon = Depends(get_coupon_by_name),
    superuser: User = Depends(superuser),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.activate_coupon(
        coupon=coupon,
        session=session,
    )


@router.patch(path='/deactivate/{coupon_name}',
              description='Деактивация купона',
              response_model=ActivityCouponeSchema,
              )
async def deactivate_coupon(
    coupon: Coupon = Depends(get_coupon_by_name),
    superuser: User = Depends(superuser),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.deactivate_coupon(
        coupon=coupon,
        session=session,
    )


@router.delete(path='/delete/{coupon_name}',
               description='Удаление купона',
               status_code=status.HTTP_204_NO_CONTENT,
               )
async def delele_coupon(
    coupon: Coupon = Depends(get_coupon_by_name),
    superuser: User = Depends(superuser),
    session: AsyncSession = Depends(db_connection.session_geter),
) -> None:
    return await crud.delete_coupon(
        coupon=coupon,
        session=session,
    )


@router.patch(path='/gift/all/{coupon_name}',
              description='Дать купон всем активным пользователям',
              response_model=CouponAddCountUser,
              )
async def gift_all_active_users(
    coupon: Coupon = Depends(get_coupon_by_name),
    superuser: User = Depends(superuser),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.gift_to_all_active_users(
        coupon=coupon,
        session=session,
    )


@router.patch(path='/gift/{user_id}/{coupon_name}',
              description='Дать купон пользователю',
              response_model=CouponViewSchema,
              )
async def gift_coupone_to_user(
    user_id: int,
    coupon: Coupon = Depends(get_coupon_by_name),
    superuser: User = Depends(superuser),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.gift_to_user(
        user_id=user_id,
        coupon=coupon,
        session=session
    )


@router.patch(path='/remove/all/{coupon_name}',
              description='Забрать купоны у всех пользователей',
              response_model=CouponAddCountUser,
              )
async def remove_coupon_all_user(
    coupon: Coupon = Depends(get_coupon_by_name),
    superuser: User = Depends(superuser),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.remove_all_coupons_from_users(
        coupon=coupon,
        session=session,
    )


@router.patch(path='/remove/{user_id}/{coupon_name}',
              description='Забрать купон у пользователя',
              response_model=CouponViewSchema,
              )
async def remove_coupone_from_user(
    user_id: int,
    superuser: User = Depends(superuser),
    coupon: Coupon = Depends(get_coupon_by_name),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.remove_from_user(
        user_id=user_id,
        coupon=coupon,
        session=session
    )
