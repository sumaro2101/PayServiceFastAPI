from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from .dependencies import get_or_create_basket
from api_v1.products.dependencies import get_product_by_id
from config.models import db_helper, Basket, Product


router = APIRouter(prefix='/basket',
                   tags=['basket'])


@router.get(path='/get/')
async def get_basket(basket: Basket = Depends(get_or_create_basket)):
    return basket


@router.put(path='/add-product/{product_id}/')
async def add_products(basket: Basket = Depends(get_or_create_basket),
                       product: Product = Depends(get_product_by_id),
                       session: AsyncSession = Depends(db_helper.session_geter)
                       ):
    return await crud.add_product_basket(basket=basket,
                                         product=product,
                                         session=session,
                                         )


@router.delete(path='/delete-product/{product_id}/')
async def delete_products(basket: Basket = Depends(get_or_create_basket),
                          product: Product = Depends(get_product_by_id),
                          session: AsyncSession = Depends(db_helper.session_geter)
                          ):
    return await crud.delete_product_basket(basket=basket,
                                            product=product,
                                            session=session,
                                            )


@router.delete(path='/delete-all-products/')
async def delete_all_products(basket: Basket = Depends(get_or_create_basket),
                              session: AsyncSession = Depends(db_helper.session_geter),
                              ):
    return await crud.delete_all_products(basket=basket,
                                          session=session,
                                          )
