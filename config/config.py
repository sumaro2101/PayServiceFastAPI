import os
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent

CERTS_DIR = BASE_DIR / 'certs'


load_dotenv('.env')

class RabbitSettings(BaseModel):
    RMQ_HOST: str = os.getenv('RMQ_HOST')
    RMQ_PORT: str = os.getenv('RMQ_PORT')
    RMQ_USER: str = os.getenv('RMQ_USER')
    RMQ_PASSWORD: str = os.getenv('RMQ_PASSWORD')


class DBSettings(BaseModel):
    url: str = os.getenv('DB_URL')


class AuthJWT(BaseModel):
    PRIVATE_KEY_PATH: Path = CERTS_DIR / 'jwt-private.pem'
    PUBLIC_KEY_PATH: Path = CERTS_DIR / 'jwt-public.pem'
    ALGORITHM: str = os.getenv('ALGORITHM_JWT_AUTH')
    EXPIRE_MINUTES: int = 10
    REFRESH_EXPIRE_MINUTES: int = ((60 * 24) * 30)
    TOKEN_TYPE_FIELD: str = 'type'
    ACCESS_TOKEN_TYPE: str = 'access'
    REFRESH_TOKEN_TYPE: str = 'refresh'


class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    rabbit: RabbitSettings = RabbitSettings()
    debug: bool = bool(int(os.getenv('DEBUG')))
    FAIL_BASIC_AUTH: str = 'Не верный логин или пароль'
    FAIL_TOKEN_AUTH: str = 'Токен не валидный'
    AUTH_JWT: AuthJWT = AuthJWT()


settings = Settings()
