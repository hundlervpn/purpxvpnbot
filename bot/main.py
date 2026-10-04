import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from . import handlers
from . import stubs
from .config import BOT_TOKEN

COMMANDS = [
    BotCommand(command="start", description="Главное меню"),
    BotCommand(command="help", description="Помощь"),
    BotCommand(command="buy", description="Покупка/продление доступа"),
    BotCommand(command="offer", description="Оферта"),
]


async def _serve() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    )
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    me = await bot.get_me()
    stubs.BOT_USERNAME = me.username  # для реф. ссылок вместо хардкода
    await bot.set_my_commands(COMMANDS)  # панель «Меню» у поля ввода
    dp = Dispatcher()
    dp.include_router(handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Бот @%s запущен (long polling)", me.username)
    await dp.start_polling(bot)


def run() -> None:
    try:
        asyncio.run(_serve())
    except (KeyboardInterrupt, SystemExit):
        logging.getLogger(__name__).info("Бот остановлен")
