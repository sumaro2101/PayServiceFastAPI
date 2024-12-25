from fastapi import APIRouter, Depends, status
from fastapi_users.router.common import ErrorModel
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from .common import ErrorCode
from .dependencies import get_or_create_basket
from api_v1.products.dependencies import get_product_by_id
from api_v1.auth.permissions import active_user
from api_v1.users.dao import UserDAO
from config.database import db_connection
from config.models import Basket, Product, User
from .schemas import CouponeNameSchema, BaseBasketSchema, LinkToPayment


router = APIRouter(prefix='/basket',
                   tags=['Basket'])


@router.get(path='/get',
            name='basket:get',
            response_model=BaseBasketSchema,
            dependencies=[Depends(active_user)],
            responses={
                status.HTTP_401_UNAUTHORIZED: {
                    "description": "Missing token or inactive user.",
                    },
                },
            )
async def get_basket(basket: Basket = Depends(get_or_create_basket)):
    return basket


@router.put(path='/buy',
            name='basket:buy',
            dependencies=[Depends(active_user)],
            response_model=LinkToPayment,
            responses={
                status.HTTP_401_UNAUTHORIZED: {
                    "description": "Missing token or inactive user.",
                    },
                status.HTTP_400_BAD_REQUEST: {
                    'model': ErrorModel,
                    'content': {
                        'application/json': {
                            'examples': {
                                ErrorCode.COUPON_ALREADY_USED: {
                                    'summary': 'Coupon is used.',
                                    'value': {
                                        'detail': ErrorCode.COUPON_ALREADY_USED,
                                        }
                                    },
                                ErrorCode.COUPON_NOT_HAVE_USER: {
                                    'summary': 'User not found from user',
                                    'value': {
                                        'detail': ErrorCode.COUPON_NOT_HAVE_USER,
                                        }
                                    },
                                ErrorCode.ZERO_PRODUCTS_IN_BASKET: {
                                    'summary': 'Zero products in basket',
                                    'value': {
                                        'detail': ErrorCode.ZERO_PRODUCTS_IN_BASKET,
                                        }
                                    },
                                ErrorCode.STRIPE_PAYMENT_ERRORS: {
                                    'summary': 'Individual Errors Stripe',
                                    'value': {
                                        'detail': ErrorCode.STRIPE_PAYMENT_ERRORS,
                                        }
                                    },
                                }
                            }
                        }
                    },
                },
            )
async def buy_products(
    coupon: CouponeNameSchema,
    user: User = Depends(active_user),
    basket: Basket = Depends(get_or_create_basket),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    user_with_coupon = await UserDAO.find_item_by_args(
        session=session,
        id=user.id,
        many_to_many=(User.coupons,),
    )
    payment = crud.Payment(
        coupon=coupon.coupon_name,
        user=user_with_coupon,
        basket=basket,
        session=session,
    )
    payment_session = await payment.get_session()
    return {'link': payment_session.url}


@router.put(path='/add-product/{product_id}')
async def add_products(
    basket: Basket = Depends(get_or_create_basket),
    product: Product = Depends(get_product_by_id),
    session: AsyncSession = Depends(db_connection.session_geter)
):
    return await crud.add_product_basket(
        basket=basket,
        product=product,
        session=session,
        )


@router.delete(path='/delete-product/{product_id}')
async def delete_products(
    basket: Basket = Depends(get_or_create_basket),
    product: Product = Depends(get_product_by_id),
    session: AsyncSession = Depends(db_connection.session_geter)
):
    return await crud.delete_product_basket(
        basket=basket,
        product=product,
        session=session,
        )


@router.delete(path='/delete-all-products')
async def delete_all_products(
    basket: Basket = Depends(get_or_create_basket),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.delete_all_products(
        basket=basket,
        session=session,
        )
