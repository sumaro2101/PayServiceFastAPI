from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from config.models.user import User

from . import crud
from .dependencies import get_or_create_basket
from api_v1.products.dependencies import get_product_by_id
from api_v1.auth.auth_validators import get_current_active_user
from config.database import db_connection
from config.models import Basket, Product
from .schemas import CouponeNameSchema


router = APIRouter(prefix='/basket',
                   tags=['Basket'])


@router.get(path='/get/')
async def get_basket(basket: Basket = Depends(get_or_create_basket)):
    return basket


@router.put(path='/buy/')
async def buy_products(coupone: CouponeNameSchema,
                       user: User = Depends(get_current_active_user),
                       basket: Basket = Depends(get_or_create_basket),
                       session: AsyncSession = Depends(db_connection.session_geter),
                       ):
    payment = crud.Payment(
        coupon=coupone,
        user=user,
        basket=basket,
        session=session,
    )
    payment_session = await payment.get_session()
    return dict(state='success',
                url_payment=payment_session.url,
                )


@router.put(path='/add-product/{product_id}/')
async def add_products(basket: Basket = Depends(get_or_create_basket),
                       product: Product = Depends(get_product_by_id),
                       session: AsyncSession = Depends(db_connection.session_geter)
                       ):
    return await crud.add_product_basket(basket=basket,
                                         product=product,
                                         session=session,
                                         )


@router.delete(path='/delete-product/{product_id}/')
async def delete_products(basket: Basket = Depends(get_or_create_basket),
                          product: Product = Depends(get_product_by_id),
                          session: AsyncSession = Depends(db_connection.session_geter)
                          ):
    return await crud.delete_product_basket(basket=basket,
                                            product=product,
                                            session=session,
                                            )


@router.delete(path='/delete-all-products/')
async def delete_all_products(basket: Basket = Depends(get_or_create_basket),
                              session: AsyncSession = Depends(db_connection.session_geter),
                              ):
    return await crud.delete_all_products(basket=basket,
                                          session=session,
                                          )
