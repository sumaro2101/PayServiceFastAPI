import os
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent

CERTS_DIR = BASE_DIR / 'certs'


load_dotenv('.env')

class StripeSettings(BaseModel):
    API_KEY: str = os.getenv('STRIPE_API')


class RabbitSettings(BaseModel):
    RMQ_HOST: str = os.getenv('RMQ_HOST')
    RMQ_PORT: str = os.getenv('RMQ_PORT')
    RMQ_USER: str = os.getenv('RABBITMQ_DEFAULT_USER')
    RMQ_PASSWORD: str = os.getenv('RABBITMQ_DEFAULT_PASS')
    broker_url: str = ('amqp://' +
                       RMQ_USER +
                       ':' +
                       RMQ_PASSWORD +
                       '@' +
                       RMQ_HOST +
                       ':' +
                       RMQ_PORT)
    DEFAULT_QUEUE: str = 'rabbit_test'


class DBSettings(BaseModel):
    _engine: str = os.getenv('DB_ENGINE')
    _owner: str = os.getenv('DB_USER')
    _password: str = os.getenv('DB_PASSWORD')
    _name: str = os.getenv('DB_HOST')
    _db_name: str = os.getenv('DB_NAME')
    url: str = f'{_engine}://{_owner}:{_password}@{_name}/{_db_name}'


class AuthJWT(BaseModel):
    PRIVATE_KEY_PATH: Path = CERTS_DIR / 'jwt-private.pem'
    PUBLIC_KEY_PATH: Path = CERTS_DIR / 'jwt-public.pem'
    ALGORITHM: str = os.getenv('ALGORITHM_JWT_AUTH')
    EXPIRE_MINUTES: int = 60
    REFRESH_EXPIRE_MINUTES: int = ((60 * 24) * 30)
    TOKEN_TYPE_FIELD: str = 'type'
    ACCESS_TOKEN_TYPE: str = 'access'
    REFRESH_TOKEN_TYPE: str = 'refresh'


class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    # LIFESPAN_TOKEN: int = 60 * 5
    RANDBITS: int = 41
    db: DBSettings = DBSettings()
    rabbit: RabbitSettings = RabbitSettings()
    debug: bool = bool(int(os.getenv('DEBUG')))
    FAIL_BASIC_AUTH: str = 'Не верный логин или пароль'
    FAIL_TOKEN_AUTH: str = 'Токен не валидный'
    AUTH_JWT: AuthJWT = AuthJWT()
    STRIPE: StripeSettings = StripeSettings()


settings = Settings()
