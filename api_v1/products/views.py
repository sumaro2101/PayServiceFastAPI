from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from .schemas import (Product,
                      ProductCreate,
                      ProductUpdate,
                      ActivityProductSchema,
                      )
from api_v1.auth.permissions import superuser
from config.database import db_connection
from .dependencies import get_product_by_id


router = APIRouter(prefix='/products',
                   tags=['Products'],
                   )


@router.post('/create',
             name='products:create',
             response_model=Product,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(superuser)],
             responses={
                 status.HTTP_401_UNAUTHORIZED: {
                        "description": "Missing token or inactive user.",
                 },
                 status.HTTP_403_FORBIDDEN: {
                        "description": "Not a superuser.",
                 },
             },
             )
async def create_product_api_view(
    product: ProductCreate,
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.product_create(session=session,
                                     product=product,
                                     )


@router.patch('/{product_id}/update',
              name='products:patch',
              response_model=Product,
              dependencies=[Depends(superuser)],
              responses={
                 status.HTTP_401_UNAUTHORIZED: {
                     "description": "Missing token or inactive user.",
                 },
                 status.HTTP_403_FORBIDDEN: {
                     "description": "Not a superuser.",
                 },
                 status.HTTP_404_NOT_FOUND: {
                     "description": "Product not found.",
                 },
              },
              )
async def update_product_api_view(
    product_update: ProductUpdate,
    product: Product = Depends(get_product_by_id),
    session: AsyncSession = Depends(db_connection.session_geter),
) -> Product:
    return await crud.product_update(product=product,
                                     product_update=product_update,
                                     session=session,
                                     )


@router.patch('/{product_id}/activate',
              name='products:activate',
              response_model=ActivityProductSchema,
              dependencies=[Depends(superuser)],
              responses={
                 status.HTTP_400_BAD_REQUEST: {
                     "description": "Product is already active.",
                 },
                 status.HTTP_401_UNAUTHORIZED: {
                     "description": "Missing token or inactive user.",
                 },
                 status.HTTP_403_FORBIDDEN: {
                     "description": "Not a superuser.",
                 },
                 status.HTTP_404_NOT_FOUND: {
                     "description": "Product not found.",
                 },
              },
              )
async def activate_product_api_view(
    product: Product = Depends(get_product_by_id),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.product_activate(session=session,
                                       product=product,
                                       )


@router.patch('/{product_id}/deactivate',
              name='products:deactivate',
              response_model=ActivityProductSchema,
              dependencies=[Depends(superuser)],
              responses={
                 status.HTTP_400_BAD_REQUEST: {
                     "description": "Product is already not active.",
                 },
                 status.HTTP_401_UNAUTHORIZED: {
                     "description": "Missing token or inactive user.",
                 },
                 status.HTTP_403_FORBIDDEN: {
                     "description": "Not a superuser.",
                 },
                 status.HTTP_404_NOT_FOUND: {
                     "description": "Product not found.",
                 },
              },
              )
async def deactivate_product_api_view(
    product: Product = Depends(get_product_by_id),
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.product_deactivate(product=product,
                                         session=session,
                                         )


@router.get('/list',
            name='products:list',
            response_model=list[Product],
            )
async def list_products_api_view(
    session: AsyncSession = Depends(db_connection.session_geter),
):
    return await crud.get_products(session=session)


@router.get('/{product_id}',
            name='products:get',
            response_model=Product,
            responses={
                 status.HTTP_404_NOT_FOUND: {
                     "description": "Product not found.",
                 },
              },
            )
async def product_api_view(
    product: Product = Depends(get_product_by_id),
) -> Product:
    return product
