import aio_pika
from config.config import settings
from loguru import logger

connection_params = dict(
    host=settings.rabbit.RMQ_HOST,
    port=int(settings.rabbit.RMQ_PORT),
    login=settings.rabbit.RMQ_USER,
    password=settings.rabbit.RMQ_PASSWORD,
)


async def get_connection() -> aio_pika.connect:
    return await aio_pika.connect(**connection_params)

async def get_channel(connect: aio_pika.connect) -> aio_pika.Channel:
    return await aio_pika.Channel(connection=connect)


class ConnectMQ:
    """
    Соединение с сервером RabbitMQ
    """

    def __init__(self) -> None:
        self._connection = None
        self._channel = None

    async def consume(self, loop):
        self._connection = await aio_pika.connect_robust(
            host=settings.rabbit.RMQ_HOST,
            port=int(settings.rabbit.RMQ_PORT),
            login=settings.rabbit.RMQ_USER,
            password=settings.rabbit.RMQ_PASSWORD,
            loop=loop,
        )
        self._channel = await self._connection.channel()
        queue = await self._channel.declare_queue('test')
        return self._connection


mq_connect = ConnectMQ()
