from fastapi import FastAPI

from config import settings
from api_v1.users.views import router as users
from .products.views import router as products
from .users.views import router as users
from .posts.views import router as posts
from .orders.views import router as orders
from .auth.views import router as auth
from .basket.views import router as basket
from .payments.views import router as payment
from .promos.views import router as promos


def register_routers(app: FastAPI) -> None:
    """
    Функция по регистрации роутеров
    """
    app.include_router(
        router=users,
        prefix=settings.API_PREFIX,
        )
    app.include_router(
        router=products,
        prefix=settings.API_PREFIX,
        )
    app.include_router(
        router=posts,
        prefix=settings.API_PREFIX,
        )
    app.include_router(
        router=orders,
        prefix=settings.API_PREFIX,
        )
    app.include_router(
        router=auth,
        prefix=settings.API_PREFIX,
        )
    app.include_router(
        router=basket,
        prefix=settings.API_PREFIX,
        )
    app.include_router(
        router=payment,
        prefix=settings.API_PREFIX,
        )
    app.include_router(
        router=promos,
        prefix=settings.API_PREFIX,
        )
