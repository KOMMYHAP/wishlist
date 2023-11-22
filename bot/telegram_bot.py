#!/usr/bin/python
import argparse
import logging

from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage

from bot.filters.setup_filters import setup_filters
from bot.handlers.setup_handlers import setup_handlers
from bot.middlewares.setup_middlewares import setup_middlewares
from bot.utilities.bot_exception_handler import DebugExceptionHandler
from wish.state_adapters.state_storage_adapter import StateStorageAdapter
from wish.storage_adapters.file_storage_adapter import WishStorageFileAdapter
from wish.wish_manager import WishManager


async def entry_point() -> None:
    parser = argparse.ArgumentParser("WishList telegram bot")
    parser.add_argument('-t', '--token', required=True)
    parser.add_argument('-f', '--storage-file', required=True)
    args = parser.parse_args()

    root_logger = logging.getLogger()
    state_storage = StateMemoryStorage()
    state_adapter = StateStorageAdapter(state_storage, root_logger)
    wish_storage = WishStorageFileAdapter(args.storage_file)
    wish_manager = WishManager(wish_storage, root_logger)

    bot = AsyncTeleBot(args.token, exception_handler=DebugExceptionHandler(), state_storage=state_storage)

    setup_filters(bot)
    setup_middlewares(bot, root_logger, state_adapter, wish_manager)
    setup_handlers(bot)

    await bot.polling(non_stop=True)
