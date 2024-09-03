import os

from pydantic_settings import BaseSettings
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv('.env')

class DBSettings(BaseModel):
    url: str = os.getenv('DB_URL')


class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    debug: bool = bool(int(os.getenv('DEBUG')))


settings = Settings()
