from fastapi import APIRouter, status, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from config.models import db_helper

from . import crud
from .schemas import (Product,
                      ProductCreate,
                      ProductUpdate,
                      ActivityProductSchema,
                      )
from config.models.db_helper import db_helper
from .dependencies import get_product_by_id


router = APIRouter(prefix='/products',
                   tags=['Products'],
                   )


@router.post('/create/',
             name='Создание продукта',
             response_model=Product,
             status_code=status.HTTP_201_CREATED,
             )
async def create_product_api_view(product: ProductCreate,
                                  session: AsyncSession = Depends(db_helper.session_geter),
                                  ):
    return await crud.product_create(session=session,
                                     product=product,
                                     )


@router.patch('/{product_id}/update/',
              name='Обновление продукта',
              response_model=Product,
              )
async def update_product_api_view(product_update: ProductUpdate,
                                  product: Product = Depends(get_product_by_id),
                                  session: AsyncSession = Depends(db_helper.session_geter),
                                  ) -> Product:
    return await crud.product_update(product=product,
                                     product_update=product_update,
                                     session=session,
                                     )


@router.patch('/{product_id}/activate/',
              name='Активация продутка',
              response_model=ActivityProductSchema,
              )
async def activate_product_api_view(product: Product = Depends(get_product_by_id),
                                    session: AsyncSession = Depends(db_helper.session_geter),
                                    ):
    return await crud.product_activate(session=session,
                                       product=product,
                                       )


@router.patch('/{product_id}/deactivate/',
               name='Деативация продукта',
               response_model=ActivityProductSchema,
               )
async def deactivate_product_api_view(
    product: Product = Depends(get_product_by_id),
    session: AsyncSession = Depends(db_helper.session_geter),
    ):
    return await crud.product_deactivate(product=product,
                                         session=session,
                                         )


@router.get('/list/',
            name='Получение списка продуктов',
            response_model=list[Product],
            )
async def list_products_api_view(session: AsyncSession = Depends(db_helper.session_geter)):
    return await crud.get_products(session=session)


@router.get('/{product_id}/',
            name='Получение продукта',
            response_model=Product,
            )
async def product_api_view(product: Product = Depends(get_product_by_id)) -> Product:
    return product
