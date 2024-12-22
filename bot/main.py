from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot.app import register_router
from bot.bot_config import bot_settings
from config import settings


def start_bot():
    bot = Bot(token=settings.API_BOT,
              default=DefaultBotProperties(
                  parse_mode=bot_settings.PARSE_MODE,
                  link_preview_prefer_small_media=True,
              ))
    dispatcher = Dispatcher()
    register_router(dispatcher=dispatcher)
    dispatcher.run_polling(bot)


if __name__ == '__main__':
    start_bot()
