import os
from pydantic_settings import BaseSettings
from aiogram.enums import ParseMode


class Settings(BaseSettings):
    API_BOT: str = os.getenv('API_BOT')
    ATTEMPTS: int = 5
    PARSE_MODE: str = ParseMode.HTML


bot_settings = Settings()
