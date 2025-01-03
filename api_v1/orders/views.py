from fastapi import APIRouter, Depends, status, HTTPException
from fastapi_users.router.common import ErrorModel
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.permissions import superuser, active_user
from .schemas import (OrderCreateSchema,
                      OrderUpdateSchema,
                      ReadOrder,
                      )
from . import crud
from config.database import db_connection
from config.models import Order, User
from .dependencies import get_order_by_id
from .common import ErrorCode


router = APIRouter(prefix='/orders',
                   tags=['Orders'],
                   )


@router.post('/create',
             name='orders:create',
             status_code=status.HTTP_201_CREATED,
             response_model=ReadOrder,
             dependencies=[Depends(superuser)],
             responses={
                 status.HTTP_401_UNAUTHORIZED: {
                     "description": "Missing token or inactive user.",
                 },
                 status.HTTP_403_FORBIDDEN: {
                     "description": "Not a superuser.",
                 },
                 status.HTTP_400_BAD_REQUEST: {
                     "description": "Empty list products.",
                 },
                 status.HTTP_404_NOT_FOUND: {
                       'model': ErrorModel,
                       'content': {
                          'application/json': {
                              'examples': {
                                  ErrorCode.NOT_FOUND_PRODUCTS: {
                                      'summary': 'Not found some products',
                                      'value': {
                                          'code': ErrorCode.NOT_FOUND_PRODUCTS,
                                          'reason': 'Not found products ids 1, 2, 3',
                                          }
                                      },
                                  }
                              }
                          }
                       },
                 },
             )
async def create_order_api_view(
    order: OrderCreateSchema,
    user: User = Depends(superuser),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.create_order(
        order_schema=order,
        user_id=user.id,
        session=session,
        )


@router.patch('/{order_id}/update',
              name='orders:patch',
              dependencies=[Depends(superuser)],
              response_model=ReadOrder,
              responses={
                 status.HTTP_401_UNAUTHORIZED: {
                     "description": "Missing token or inactive user.",
                 },
                 status.HTTP_403_FORBIDDEN: {
                     "description": "Not a superuser.",
                 },
                 status.HTTP_400_BAD_REQUEST: {
                     "description": "Empty list products.",
                 },
                 status.HTTP_404_NOT_FOUND: {
                       'model': ErrorModel,
                       'content': {
                          'application/json': {
                              'examples': {
                                  ErrorCode.NOT_FOUND_PRODUCTS: {
                                      'summary': 'Not found some products',
                                      'value': {
                                          'code': ErrorCode.NOT_FOUND_PRODUCTS,
                                          'reason': 'Not found products ids 1, 2, 3',
                                          }
                                      },
                                  }
                              }
                          }
                       },
                 },
              )
async def update_order_api_view(
    attrs: OrderUpdateSchema,
    order: Order = Depends(get_order_by_id),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.update_order(session=session,
                                   order=order,
                                   attrs=attrs)


@router.get('',
            name='orders:list',
            dependencies=[Depends(superuser)],
            response_model=list[ReadOrder],
            responses={
                 status.HTTP_401_UNAUTHORIZED: {
                     "description": "Missing token or inactive user.",
                 },
                 status.HTTP_403_FORBIDDEN: {
                     "description": "Not a superuser.",
                 },
            },
            )
async def list_orders_api_view(
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.list_orders(session=session)


@router.get(path='/get/{order_id}',
            name='orders:get',
            dependencies=[Depends(active_user)],
            response_model=ReadOrder,
            responses={
                 status.HTTP_401_UNAUTHORIZED: {
                     "description": "Missing token or inactive user.",
                 },
                 status.HTTP_403_FORBIDDEN: {
                     "description": "Permisson Denied for this order."
                 },
                 status.HTTP_404_NOT_FOUND: {
                     "description": "Order not found",
                 },
            },
            )
async def get_order_api_view(order: Order = Depends(get_order_by_id),
                             user: User = Depends(active_user),
                             ):
    if not user.is_superuser and order.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=ErrorCode.PERMISSION_DENIED,
                            )
    return order


@router.delete('/{order_id}/delete',
               name='order:delete',
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
                     "description": "Order not found",
                 },
                 },
               )
async def delete_order_api_view(
    session: AsyncSession = Depends(db_connection.session_geter),
    order: Order = Depends(get_order_by_id),
):
    await crud.delete_order(
        session=session,
        order=order,
    )
