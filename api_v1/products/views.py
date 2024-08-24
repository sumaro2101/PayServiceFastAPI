from fastapi import Path, APIRouter, HTTPException, status, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from config.models import db_helper

from . import crud
from .schemas import Product, ProductCreate, ProductUpdate
from config.models.db_helper import db_helper
from .dependencies import get_product_by_id


router = APIRouter(prefix='/products',
                   tags=['products'],
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
                                     session=session
                                     )


@router.delete('/{product_id}/delete/',
               name='Удаление продукта',
               responses=None,
               status_code=status.HTTP_204_NO_CONTENT,
               )
async def delete_product_api_view(
    product: Product = Depends(get_product_by_id),
    session: AsyncSession = Depends(db_helper.session_geter),
    ) -> None:
    await crud.product_delete(product=product,
                              session=session)


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
