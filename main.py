from fastapi import FastAPI
from contextlib import asynccontextmanager

from config.models.base import Base
from config.models.db_helper import db_helper
from api_v1 import register_routers
from app_includes import (
    register_errors,
    register_middlewares,
)


def start_app() -> FastAPI:
    """
    Создание приложения со всеми настройками
    """
    app = FastAPI(lifespan=lifespan)
    register_routers(app=app)
    register_errors(app=app)
    register_middlewares(app=app)
    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
    await db_helper.dispose()


app = start_app()
