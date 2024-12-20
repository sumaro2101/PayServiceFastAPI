from random import randint
from aiogram import Router, F, html
from aiogram.types import Message

from bot.app.numbers.user_stat import user
from bot.bot_config import bot_settings


router = Router(name='Numbers')


def get_random_number() -> int:
    return randint(1, 100)


@router.message(F.text.lower().in_((
    'да',
    'давай',
    'сыграем',
    'игра',
    'играть',
    'хочу играть',
)))
async def process_positive_answer(message: Message):
    if not user['in_game']:
        user['in_game'] = True
        user['sectet_number'] = get_random_number()
        user['attempts'] = bot_settings.ATTEMPTS
        await message.answer(
            'Ура!\n\nЯ загадал число от 1 до 100, '
            'попробуй угадать!',
        )
    else:
        await message.answer(
            'Пока мы играем в игру я могу '
            'реагировать только на числа от 1 до 100 '
            'и команды /cancel и /stat',
        )


@router.message(F.text.lower().in_(
    (
        'нет',
        'не',
        'не хочу',
        'не буду',
    )
))
async def process_negative_answer(message: Message):
    if not user['in_game']:
        await message.answer('Мы еще не играем. Хотите сыграть?')
    else:
        await message.answer(
            'Жаль :(\n\nЕсли захотите поиграть - просто '
            'напишите об этом',
        )


@router.message(F.text)
async def process_entites_answer(message: Message):
    data = dict(
        url='<N/A>',
        email='<N/A>',
        code='<N/A>',
    )
    entities = message.entities or []
    for item in entities:
        if item.type in data.keys():
            data[item.type] = item.extract_from(message.text)
    await message.reply(
        "Вот что я нашёл:\n"
        f"URL: {html.quote(data['url'])}\n"
        f"E-mail: {html.quote(data['email'])}\n"
        f"Пароль: {html.quote(data['code'])}"
    )


@router.message(F.animation)
async def process_animation_answer(message: Message):
    await message.reply_animation(message.animation.file_id)
