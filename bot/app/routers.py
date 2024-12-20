from aiogram import Dispatcher

from bot.app.numbers.endpoints import router as numbers
from bot.app.commands.endpoints import router as commands


def register_router(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(commands)
    dispatcher.include_router(numbers)
