from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from starlette.config import Config


base_dir = Path(__file__).resolve().parent.parent
log_dir = base_dir.joinpath('logs')
certs_dir = base_dir / 'certs'

config = Config('.env')


class StripeSettings(BaseModel):
    """
    Настройки Stripe
    """

    API_KEY: str = config('STRIPE_API')
    STRIPE_ORIGIN: str = config('STRIPE_ORIGIN')


class JWTSettings(BaseModel):
    """
    Настройки JWT токена
    """
    NAME: str = 'jwt'
    SECRET: str = config('SECRET_KEY')
    RESET_LIFESPAN_TOKEN_SECONDS: int = 3600
    JWT_PATH: str = '/auth'


class RabbitSettings(BaseModel):
    """
    Настройки RabbitMQ
    """

    RMQ_HOST: str = config('RMQ_HOST')
    RMQ_PORT: str = config('RMQ_PORT')
    RMQ_USER: str = config('RABBITMQ_DEFAULT_USER')
    RMQ_PASSWORD: str = config('RABBITMQ_DEFAULT_PASS')
    broker_url: str = ('amqp://' +
                       RMQ_USER +
                       ':' +
                       RMQ_PASSWORD +
                       '@' +
                       RMQ_HOST +
                       ':' +
                       RMQ_PORT)
    DEFAULT_QUEUE: str = 'rabbit_test'


class TestDBSettings(BaseModel):
    """
    Настройки тестовой базы данных
    """

    _engine: str = config('TEST_DB_ENGINE')
    _owner: str = config('TEST_DB_USER')
    _password: str = config('TEST_DB_PASSWORD')
    _name: str = config('TEST_DB_HOST')
    _db_name: str = config('TEST_DB_NAME')
    url: str = f'{_engine}://{_owner}:{_password}@{_name}/{_db_name}'


class DBSettings(BaseModel):
    """
    Настройки DataBase
    """

    _engine: str = config('DB_ENGINE')
    _owner: str = config('DB_USER')
    _password: str = config('DB_PASSWORD')
    _name: str = config('DB_HOST')
    _db_name: str = config('DB_NAME')
    url: str = f'{_engine}://{_owner}:{_password}@{_name}/{_db_name}'


class Settings(BaseSettings):
    """
    Настройки проекта
    """

    model_config = SettingsConfigDict(
        extra='ignore',
    )
    SECRET_KEY: str = config('SECRET_KEY')
    # LIFESPAN_TOKEN: int = 60 * 5
    RANDBITS: int = 41
    db: DBSettings = DBSettings()
    test_db: TestDBSettings = TestDBSettings()
    rabbit: RabbitSettings = RabbitSettings()
    JWT: JWTSettings = JWTSettings()
    debug: bool = bool(int(config('DEBUG')))
    STRIPE: StripeSettings = StripeSettings()
    API_PREFIX: str = '/api/v1'
    BASE_DIR: Path = base_dir
    LOG_DIR: Path = log_dir
    CURRENT_ORIGIN: str = config('CURRENT_ORIGIN')
    API_BOT: str = config('API_BOT')


settings = Settings()
