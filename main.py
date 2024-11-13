from fastapi import FastAPI
from contextlib import asynccontextmanager
from config.models.base import Base
from config.models.db_helper import db_helper
from api_v1 import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
    await db_helper.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
