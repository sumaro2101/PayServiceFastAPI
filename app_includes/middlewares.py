from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from config import settings


def register_middlewares(app: FastAPI) -> None:
    """
    Регистрация middleware
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            settings.CURRENT_ORIGIN,
            settings.STRIPE.STRIPE_ORIGIN,
        ],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
