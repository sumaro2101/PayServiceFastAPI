from fastapi import FastAPI
from contextlib import asynccontextmanager

from config.models.base import Base
from config.database import db_connection
from api_v1 import register_routers
from app_includes import (
    register_errors,
    register_middlewares,
    register_prometheus,
)


def start_app() -> FastAPI:
    """
    Создание приложения со всеми настройками
    """
    app = FastAPI(lifespan=lifespan)
    register_routers(app=app)
    register_errors(app=app)
    register_middlewares(app=app)
    register_prometheus(app=app)
    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_connection.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
    await db_connection.dispose()


app = start_app()
