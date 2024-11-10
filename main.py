from fastapi import FastAPI
from contextlib import asynccontextmanager
import aio_pika
from config.models.base import Base
from config.models.db_helper import db_helper
from config.rabbitmq.connection import mq_connect
from api_v1 import router
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        loop = asyncio.get_running_loop()
        task = loop.create_task(mq_connect.consume(loop))
        await task
        yield
    await db_helper.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.get('/')
def hello_index():
    return {
        'message': 'Hello index!',
    }
