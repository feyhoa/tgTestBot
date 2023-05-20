import asyncio
import requests

import re
from enum import Enum

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
from config import BOT_TOKEN, ADMINS

mainloop = asyncio.new_event_loop()
asyncio.set_event_loop(mainloop)


# chatLowMatterBot = Bot(BOT_TOKEN, parse_mode="HTML")
# dispatcher = Dispatcher(chatLowMatterBot, loop=mainloop)


class BotModes(Enum):
    DEFAULT = 0
    STATISTICS = 1
    LINK = 2


class ChatBot(Bot):
    def __init__(self, token, **kwargs):
        super().__init__(token, **kwargs)
        self.modes_db: dict = {}


chatLowMatterBot = ChatBot(token=BOT_TOKEN, parse_mode="HTML")
dispatcher = Dispatcher(chatLowMatterBot, loop=mainloop)


async def notify_admins_start(dp) -> None:
    for admin in ADMINS:
        await chatLowMatterBot.send_message(chat_id=admin,
                                            text=f"Бот запущен")


async def notify_admins_end(dp) -> None:
    for admin in ADMINS:
        await chatLowMatterBot.send_message(chat_id=admin,
                                            text=f"Бот остановлен")


@dispatcher.message_handler(commands=['start'])
async def start_command_answer(message: Message) -> None:
    chatLowMatterBot.modes_db[message.from_user.id] = BotModes.DEFAULT
    await message.answer(text=f"Привет, {message.from_user.first_name}!\n"
                              f"Перед тем, как мы познакомимся получше, я расскажу о режимах своей работы:\n\n"
                              f"1. Получение статистики сообщения (кол-во слов, предложений, гласных и согласных). "
                              f"Работает только с русским алфавитом.\n"
                              f"Функцию №1 возможно включить командой '/statistics'.\n\n"
                              f"2. Проверка возможности загрузки по ссылке в тексте."
                              f"Находит только первую ссылку в введённом тексте!\n"
                              f"Функцию №2 возможно включить командой '/link'.")


@dispatcher.message_handler(commands=['help'])
async def help_command_answer(message: Message) -> None:
    await message.answer(text=f"1. Получение статистики сообщения (кол-во слов, предложений, гласных и согласных). "
                              f"Работает только с русским алфавитом.\n"
                              f"Функцию №1 возможно включить командой '/statistics'.\n\n"
                              f"2. Проверка возможности загрузки по ссылке в тексте. "
                              f"Находит только первую ссылку в введённом тексте!\n"
                              f"Функцию №2 возможно включить командой '/link'.")


@dispatcher.message_handler(commands=['statistics'])
async def switch_mode_statistics(message: Message) -> None:
    chatLowMatterBot.modes_db[message.from_user.id] = BotModes.STATISTICS
    await message.answer(text=f"Включен режим получения статистики о сообщении.")


@dispatcher.message_handler(commands=['link'])
async def switch_mode_link(message: Message) -> None:
    chatLowMatterBot.modes_db[message.from_user.id] = BotModes.LINK
    await message.answer(text=f"Включен режим проверки загрузки по ссылке.")


@dispatcher.message_handler()
async def echo(message: Message) -> None:
    if message.from_user.id in chatLowMatterBot.modes_db.keys():
        message_mode = chatLowMatterBot.modes_db[message.from_user.id]
    else:
        chatLowMatterBot.modes_db[message.from_user.id] = BotModes.DEFAULT
        message_mode = BotModes.DEFAULT

    match message_mode:
        case BotModes.STATISTICS:
            text = message.text

            split_regex = re.compile(r'[.|!|?|…]')
            sentences = list(filter(lambda t: t, [t.strip() for t in split_regex.split(text)]))
            sentence_count = len(sentences)

            split_regex_words = re.compile(r'[,|;|:| ]')
            word_count: int = 0
            for sentence in sentences:
                word_count += len(list(filter(lambda t: t, [t.strip() for t in split_regex_words.split(sentence)])))

            vowels_count = len([letter for letter in text if letter.lower() in 'ыуеаоэяиюё'])

            consonants_count = len([letter for letter in text if letter.lower() in 'йцкнгшщзхъфвпрлджчсмтьб'])

            await message.reply(text=f"Статистика сообщения:\n"
                                     f"кол-во предложений: {sentence_count};\n"
                                     f"кол-во слов: {word_count};\n"
                                     f"кол-во гласных букв: {vowels_count};\n"
                                     f"кол-во согласных букв: {consonants_count}.")

        case BotModes.LINK:
            text = message.text
            link = re.search("(?P<url>https?://[^\s]+)", text).group("url")
            if link:
                res = requests.head(link, allow_redirects=True)

                if 'text/html' in res.headers['content-type']:
                    await message.reply(text=f"По этой ссылке ({link}) нет скачивания.")
                else:
                    await message.reply(text=f"По этой ссылке ({link}) идёт скачивание содержимого.")

            else:
                await message.reply(f"В этом тексте нет ссылки!")

        case _:
            await message.answer(text=f"Не выбран режим работы, если возникли проблемы с выбором, то "
                                      f"используйте команду '/help'.")
