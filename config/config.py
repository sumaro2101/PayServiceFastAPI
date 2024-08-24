import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv('.env')


class Settings(BaseSettings):
    db_url: str = os.getenv('DB_URL')
    debug: bool = bool(int(os.getenv('DEBUG')))


settings = Settings()
