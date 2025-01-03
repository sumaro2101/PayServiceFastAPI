from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, status, Depends
from fastapi_users.router.common import ErrorModel

from .schemas import (CouponViewSchema,
                      CouponSchema,
                      CouponSchemaCreate,
                      CouponSchemaUpdate,
                      ActivityCouponeSchema,
                      CouponAddCountUser,
                      )
from . import crud
from api_v1.auth.permissions import superuser
from .dependencies import get_coupon_by_name, get_full_coupone
from .common import ErrorCode
from config.database import db_connection
from config.models import Coupon
from api_stripe.api import (CreateDiscountCoupon)


router = APIRouter(prefix='/coupons',
                   tags=['Coupons'],
                   )


@router.post(path='/create',
             name='coupons:create',
             response_model=CouponSchema,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(superuser)],
             responses={
                 status.HTTP_401_UNAUTHORIZED: {
                     "description": "Missing token or inactive user.",
                 },
                 status.HTTP_403_FORBIDDEN: {
                     "description": "Not a superuser.",
                 },
                 status.HTTP_400_BAD_REQUEST: {
                      'model': ErrorModel,
                      'content': {
                          'application/json': {
                              'examples': {
                                  ErrorCode.COUPON_IS_ALREADY_EXISTS: {
                                      'summary': 'Coupon already exists in system',
                                      'value': {
                                          'detail': ErrorCode.COUPON_IS_ALREADY_EXISTS,
                                      }
                                  }
                              }
                          }
                      }
                  }
             },
             )
async def create_coupone(
    coupon_schema: CouponSchemaCreate,
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.create_coupon(
        coupon_schema=coupon_schema,
        stripe_action=CreateDiscountCoupon,
        session=session,
    )


@router.get(path='/list',
            name='coupons:list',
            response_model=list[CouponSchema],
            dependencies=[Depends(superuser)],
            responses={
                status.HTTP_401_UNAUTHORIZED: {
                     "description": "Missing token or inactive user.",
                },
                status.HTTP_403_FORBIDDEN: {
                     "description": "Not a superuser.",
                },
            }
            )
async def get_list_promos(
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.get_list_promos(session=session)


@router.patch(path='/update/{coupon_name}',
              name='coupons:patch',
              response_model=CouponSchema,
              dependencies=[Depends(superuser)],
              responses={
                  status.HTTP_401_UNAUTHORIZED: {
                       "description": "Missing token or inactive user.",
                  },
                  status.HTTP_403_FORBIDDEN: {
                       "description": "Not a superuser.",
                  },
                  status.HTTP_404_NOT_FOUND: {
                       "description": 'Coupone not found',
                  },
                  status.HTTP_400_BAD_REQUEST: {
                      'model': ErrorModel,
                      'content': {
                          'application/json': {
                              'examples': {
                                  ErrorCode.COUPON_WITH_SOME_NAME_EXISTS: {
                                      'summary': 'Coupon is have same name with another',
                                      'value': {
                                          'detail': ErrorCode.COUPON_WITH_SOME_NAME_EXISTS,
                                      }
                                  },
                              },
                          }
                      }
                  }
              },
              )
async def update_coupon(
    coupon_schema: CouponSchemaUpdate,
    coupon: Coupon = Depends(get_coupon_by_name),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.update_coupon(
        coupon_schema=coupon_schema,
        coupon=coupon,
        session=session,
    )


@router.get(path='/get/{coupon_name}',
            name='coupons:get',
            dependencies=[Depends(superuser)],
            response_model=CouponViewSchema,
            responses={
                  status.HTTP_401_UNAUTHORIZED: {
                       "description": "Missing token or inactive user.",
                  },
                  status.HTTP_403_FORBIDDEN: {
                       "description": "Not a superuser.",
                  },
                  status.HTTP_404_NOT_FOUND: {
                       "description": 'Coupone not found',
                  },
              },
            )
async def get_coupon(coupon: Coupon = Depends(get_full_coupone)):
    return coupon


@router.patch(path='/activate/{coupon_name}',
              name='coupons:activate',
              response_model=ActivityCouponeSchema,
              dependencies=[Depends(superuser)],
              responses={
                  status.HTTP_401_UNAUTHORIZED: {
                       "description": "Missing token or inactive user.",
                  },
                  status.HTTP_403_FORBIDDEN: {
                       "description": "Not a superuser.",
                  },
                  status.HTTP_404_NOT_FOUND: {
                       "description": 'Coupone not found',
                  },
                  status.HTTP_400_BAD_REQUEST: {
                      'model': ErrorModel,
                      'content': {
                          'application/json': {
                              'examples': {
                                  ErrorCode.COUPON_IS_ALREADY_ACTIVE: {
                                      'summary': 'Coupon is already active',
                                      'value': {
                                          'detail': ErrorCode.COUPON_IS_ALREADY_ACTIVE,
                                      }
                                  },
                              }
                          }
                      }
                  }
              },
              )
async def activate_coupon(
    coupon: Coupon = Depends(get_coupon_by_name),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.activate_coupon(
        coupon=coupon,
        session=session,
    )


@router.patch(path='/deactivate/{coupon_name}',
              name='coupons:deactivate',
              response_model=ActivityCouponeSchema,
              dependencies=[Depends(superuser)],
              responses={
                  status.HTTP_401_UNAUTHORIZED: {
                       "description": "Missing token or inactive user.",
                  },
                  status.HTTP_403_FORBIDDEN: {
                       "description": "Not a superuser.",
                  },
                  status.HTTP_404_NOT_FOUND: {
                        "description": 'Coupone not found',
                  },
                  status.HTTP_400_BAD_REQUEST: {
                      'model': ErrorModel,
                      'content': {
                          'application/json': {
                              'examples': {
                                  ErrorCode.COUPON_IS_ALREADY_UNACTIVE: {
                                      'summary': 'Coupon is already unactive',
                                      'value': {
                                          'detail': ErrorCode.COUPON_IS_ALREADY_UNACTIVE,
                                      }
                                  },
                              }
                          }
                      }
                  }
              },
              )
async def deactivate_coupon(
    coupon: Coupon = Depends(get_coupon_by_name),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.deactivate_coupon(
        coupon=coupon,
        session=session,
    )


@router.delete(path='/delete/{coupon_name}',
               name='coupons:delete',
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(superuser)],
               responses={
                   status.HTTP_401_UNAUTHORIZED: {
                        "description": "Missing token or inactive user.",
                   },
                   status.HTTP_403_FORBIDDEN: {
                        "description": "Not a superuser.",
                   },
                   status.HTTP_404_NOT_FOUND: {
                        "description": 'Coupone not found',
                   },
                },
               )
async def delele_coupon(
    coupon: Coupon = Depends(get_coupon_by_name),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    await crud.delete_coupon(
        coupon=coupon,
        session=session,
    )


@router.patch(path='/gift/all/{coupon_name}',
              name='coupons:gift_all',
              response_model=CouponAddCountUser,
              dependencies=[Depends(superuser)],
              responses={
                   status.HTTP_401_UNAUTHORIZED: {
                        "description": "Missing token or inactive user.",
                   },
                   status.HTTP_403_FORBIDDEN: {
                        "description": "Not a superuser.",
                   },
                   status.HTTP_404_NOT_FOUND: {
                        "description": 'Coupone not found',
                   },
                },
              )
async def gift_all_active_users(
    coupon: Coupon = Depends(get_coupon_by_name),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.gift_to_all_active_users(
        coupon=coupon,
        session=session,
    )


@router.patch(path='/gift/{user_id}/{coupon_name}',
              name='coupons:gift_to_user',
              response_model=CouponViewSchema,
              dependencies=[Depends(superuser)],
              responses={
                   status.HTTP_401_UNAUTHORIZED: {
                        "description": "Missing token or inactive user.",
                   },
                   status.HTTP_403_FORBIDDEN: {
                        "description": "Not a superuser.",
                   },
                   status.HTTP_400_BAD_REQUEST: {
                       'model': ErrorModel,
                       'content': {
                          'application/json': {
                              'examples': {
                                  ErrorCode.COUPON_IS_UNACTIVE: {
                                      'summary': 'Coupon not active',
                                      'value': {
                                          'detail': ErrorCode.COUPON_IS_UNACTIVE,
                                      }
                                  },
                                  ErrorCode.USER_HAVE_COUPON_YET: {
                                      'summary': 'User have coupon yet',
                                      'value': {
                                          'detail': ErrorCode.USER_HAVE_COUPON_YET,
                                      }
                                  },
                              }
                          }
                       }
                   },
                   status.HTTP_404_NOT_FOUND: {
                       'model': ErrorModel,
                       'content': {
                          'application/json': {
                              'examples': {
                                  ErrorCode.COUPON_NOT_FOUND: {
                                      'summary': 'Coupon not found',
                                      'value': {
                                          'detail': ErrorCode.COUPON_NOT_FOUND,
                                      }
                                  },
                                  ErrorCode.USER_NOT_FOUND: {
                                      'summary': 'User not found',
                                      'value': {
                                          'detail': ErrorCode.USER_NOT_FOUND,
                                      }
                                  },
                              }
                          }
                       }
                   },
                },
              )
async def gift_coupone_to_user(
    user_id: int,
    coupon: Coupon = Depends(get_coupon_by_name),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.gift_to_user(
        user_id=user_id,
        coupon=coupon,
        session=session
    )


@router.patch(path='/remove/all/{coupon_name}',
              name='coupons:remove_gift_all',
              response_model=CouponAddCountUser,
              dependencies=[Depends(superuser)],
              responses={
                   status.HTTP_401_UNAUTHORIZED: {
                        "description": "Missing token or inactive user.",
                   },
                   status.HTTP_403_FORBIDDEN: {
                        "description": "Not a superuser.",
                   },
                   status.HTTP_404_NOT_FOUND: {
                        "description": 'Coupone not found',
                   },
                },
              )
async def remove_coupon_all_user(
    coupon: Coupon = Depends(get_coupon_by_name),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.remove_all_coupons_from_users(
        coupon=coupon,
        session=session,
    )


@router.patch(path='/remove/{user_id}/{coupon_name}',
              name='coupons:remove_gift_from_user',
              response_model=CouponViewSchema,
              dependencies=[Depends(superuser)],
              responses={
                   status.HTTP_401_UNAUTHORIZED: {
                        "description": "Missing token or inactive user.",
                   },
                   status.HTTP_403_FORBIDDEN: {
                        "description": "Not a superuser.",
                   },
                   status.HTTP_400_BAD_REQUEST: {
                        "description": "User not have coupon yet.",
                   },
                   status.HTTP_404_NOT_FOUND: {
                       'model': ErrorModel,
                       'content': {
                          'application/json': {
                              'examples': {
                                  ErrorCode.COUPON_NOT_FOUND: {
                                      'summary': 'Coupon not found',
                                      'value': {
                                          'detail': ErrorCode.COUPON_NOT_FOUND,
                                      }
                                  },
                                  ErrorCode.USER_NOT_FOUND: {
                                      'summary': 'User not found',
                                      'value': {
                                          'detail': ErrorCode.USER_NOT_FOUND,
                                      }
                                  },
                              }
                          }
                       }
                   },
                },
              )
async def remove_coupone_from_user(
    user_id: int,
    coupon: Coupon = Depends(get_coupon_by_name),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.remove_from_user(
        user_id=user_id,
        coupon=coupon,
        session=session
    )
