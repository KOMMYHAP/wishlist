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
from wish.storage_adapters.base_storage_adapter import WishStorageBaseAdapter
from wish.storage_adapters.file_storage_adapter import WishStorageFileAdapter
from wish.storage_adapters.postgresql.postgres_storage_adapter import PostgresStorageAdapter
from wish.wish_manager import WishManager
from wish.wishlist_config import WishlistConfig

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


def _make_storage_adapter(args, logger) -> WishStorageBaseAdapter:
    if args.storage_file and args.initial_wish_id:
        return WishStorageFileAdapter(args.storage_file, args.initial_wish_id)

    dbname = args.database_name
    user = args.database_username
    password = args.database_password
    queries_directory = args.database_queries_directory
    con = f"dbname={dbname} user={user} password={password}"
    return PostgresStorageAdapter("wishlist-bot", con, queries_directory, logger)


async def entry_point() -> None:
    parser = argparse.ArgumentParser("WishList telegram bot")
    parser.add_argument('-t', '--token', required=True)
    parser.add_argument('--wishes-per-page', type=int, default=5, required=False)
    parser.add_argument('--allow-wish-owner-sees-reservation', type=bool, default=False, required=False)
    parser.add_argument('--allow-user-sees-owned-wishlist', type=bool, default=False, required=False)
    parser.add_argument('--friends-count-on-page', type=int, default=5, required=False)

    parser.add_argument('-f', '--storage-file')
    parser.add_argument('--initial-wish-id', type=int, default=1000)

    parser.add_argument('--database-name')
    parser.add_argument('--database-username')
    parser.add_argument('--database-password')
    parser.add_argument('--database-queries-directory')
    args = parser.parse_args()

    wishlist_config = WishlistConfig(
        args.wishes_per_page,
        args.allow_wish_owner_sees_reservation,
        args.allow_user_sees_owned_wishlist,
        args.initial_wish_id,
        args.friends_count_on_page
    )

    root_logger = logging.getLogger()
    state_storage = StateMemoryStorage()
    state_adapter = StateStorageAdapter(state_storage, root_logger)
    wish_storage = _make_storage_adapter(args, root_logger)
    wish_manager = WishManager(wish_storage, root_logger, wishlist_config)

    bot = AsyncTeleBot(args.token, exception_handler=DebugExceptionHandler(), state_storage=state_storage)

    bot_user = await bot.get_me()
    root_logger.info("Starts bot @%s (id: %d)", bot_user.username, bot_user.id)

    setup_filters(bot)
    setup_middlewares(bot, root_logger, state_adapter, wish_manager)
    setup_handlers(bot)

    await bot.polling(non_stop=True)
