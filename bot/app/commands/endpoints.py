from aiogram import Router, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import (Message,
                           BotCommand,
                           LinkPreviewOptions,
                           FSInputFile,
                           BufferedInputFile,
                           URLInputFile,
                           )
from aiogram.utils.formatting import (
    Text,
    Bold,
    as_list,
    as_marked_section,
    as_key_value,
    HashTag,
    )
from pathlib import Path

from bot.bot_config import bot_settings
from bot.app.numbers.user_stat import user


router = Router(name='Replyes')


@router.message(CommandStart())
async def process_start_command(message: Message) -> None:
    user_name = message.from_user.full_name
    content = Text(
        Bold('Привет! ', user_name, '✋'),
        '\nДавайте сыграем ',
        'в игру "Угадай число"?\n\n',
        'Чтобы получить правила игры и список доступных ',
        'команд - отправьте команду /help',
    )
    await message.answer(
        **content.as_kwargs()
    )


@router.message(Command(commands=(BotCommand(command='help',
                                             description='View rules for game',
                                             ),)))
async def process_help_command(message: Message) -> None:
    await message.answer(
        'Правила игры:\n\nЯ загадываю число от 1 до 100, '
        f'а вам нужно его угадать\nУ вас есть {bot_settings.ATTEMPTS} '
        'попыток\n\nДоступные команды:\n/help - правила '
        'игры и список команд\n/cancel - выйти из игры\n'
        '/stat - посмотреть статистику\n\nДавай сыграем?'
    )


@router.message(Command(commands=(BotCommand(command='info',
                                             description='Veiw Info',
                                             ),)))
async def process_info_command(message: Message):
    content = as_list(
        as_marked_section(
            Bold('Success:'),
            'Test 1',
            'Test 3',
            'Test 4',
            marker='✅ ',
        ),
        as_marked_section(
            Bold('Failed:'),
            'Test 2',
            marker='❌ ',
        ),
        as_marked_section(
            Bold('Summary:'),
            as_key_value('Total', 4),
            as_key_value('Success', 3),
            as_key_value('Failed', 1),
            marker='    ',
        ),
        HashTag('#test'),
        sep='\n\n'
    )
    await message.answer(
        **content.as_kwargs()
    )


@router.message(Command(commands=(BotCommand(command='stat',
                                             description='Views statistic game'
                                             ),)))
async def process_stat_command(message: Message):
    await message.answer(
        f'Всего игр сыграно: {user["total_games"]}\n'
        f'Игр выиграно: {user["wins"]}',
    )


@router.message(Command(commands=(BotCommand(command='cancel',
                                             description='End Game',
                                             ),)))
async def process_cancel_command(message: Message):
    in_game = user['in_game']
    if in_game:
        user['in_game'] = False
        await message.answer(
            'Вы вышли из игры. Если захотите сыграть '
            'снова - напишите об этом',
        )
    else:
        await message.answer(
            'А мы и так с вами не играем. '
            'Может, сыграем разок?',
        )


@router.message(Command(commands=(BotCommand(command='settimer',
                                             description='Set timer',
                                             ),)))
async def process_settimer_command(message: Message,
                                   command: CommandObject,
                                   ):
    if not command.args:
        await message.answer(
            'Ошибка: не переданы аргументы',
        )
        return
    try:
        delay_time, text_to_send = command.args.split(' ', maxsplit=1)
    except ValueError:
        await message.answer(
            'Ошибка: неправильный формат команды. Пример:\n'
            '/settimer <time> <message>',
            parse_mode=None,
        )
        return
    await message.answer(
        'Таймер добавлен!\n'
        f'Время: {delay_time}\n'
        f'Текст: {text_to_send}',
    )


@router.message(Command(commands=(BotCommand(command='links',
                                             description='View links to user',
                                             ),)))
async def process_links_command(message: Message):
    links_text = (
        "https://nplus1.ru/news/2024/05/23/voyager-1-science-data"
        "\n"
        "https://t.me/telegram"
    )
    link = LinkPreviewOptions(is_disabled=True)
    await message.answer(
        f"Нет превью ссылок\n{links_text}",
        link_preview_options=link,
    )

    link = LinkPreviewOptions(
        url='https://nplus1.ru/news/2024/05/23/voyager-1-science-data',
        prefer_small_media=True,
    )
    await message.answer(
        f"Маленькое превью\n{links_text}",
        link_preview_options=link,
    )

    link = LinkPreviewOptions(
        url='https://nplus1.ru/news/2024/05/23/voyager-1-science-data',
        prefer_large_media=True,
    )
    await message.answer(
        f"Большое превью\n{links_text}",
        link_preview_options=link,
    )

    link = LinkPreviewOptions(
        url='https://nplus1.ru/news/2024/05/23/voyager-1-science-data',
        prefer_small_media=True,
        show_above_text=True,
    )
    await message.answer(
        f"Маленькое превью над текстом\n{links_text}",
        link_preview_options=link,
    )

    link = LinkPreviewOptions(
        url="https://t.me/telegram",
    )
    await message.answer(
        f"Предпросмотр не первой ссылки\n{links_text}",
        link_preview_options=link,
    )


# @router.message(Command(commands=(BotCommand(command='images',
#                                              description='Send Image to user',
#                                              ),)))
# async def process_images_command(message: Message):
#     file_ids = []
    # with open('buffer_emulation.jpg', mode='rb') as image_from_buffer:
    #     result = await message.answer_photo(
    #         BufferedInputFile(
    #             image_from_buffer.read(),
    #             filename='image from buffer.jpg',
    #         ),
    #         caption='Изобращение из буфера',
    #     )
    #     file_ids.append(result.photo[-1].file_id)

    # image_from_pc = FSInputFile(Path('image_from_ps.jpg'))
    # result = await message.reply_photo(
    #     image_from_pc,
    #     caption='Изображение из компьютера',
    # )
    # file_ids.append(result.photo[-1].file_id)

    # image_from_url = URLInputFile("https://x.com/Googleorg/photo")
    # result = await message.reply_photo(
    #     image_from_url,
    #     caption='Изображение из URL',
    # )
    # file_ids.append(result.photo[-1].file_id)
    # await message.answer("Отправленные файлы:\n"+"\n".join(file_ids))


# @router.message(Command(commands=(BotCommand(command='gif',
#                                              description='Send GIF to user',
#                                              ),)))
# async def process_git_command(message: Message):
#     await message.answer_animation(
#         animation='file_id gif',
#         caption='file',
#         show_caption_above_media=True,
#     )


@router.message(F.photo)
async def send_phono_echo(message: Message):
    await message.reply(message.photo[-1].file_id)


@router.message(F.document)
async def send_document_echo(message: Message):
    await message.reply(message.document.file_id)


@router.message(F.sticker)
async def send_sticker_echo(message: Message):
    await message.reply(message.sticker.file_id)


@router.message(F.audio)
async def send_audio_echo(message: Message) -> None:
    await message.reply(text=message.audio.file_id)


@router.message(F.voice)
async def send_voice_echo(message: Message) -> None:
    await message.reply(text=message.voice.file_id)


@router.message(F.text)
async def send_text_echo(message: Message) -> None:
    await message.reply(text=message.text)
