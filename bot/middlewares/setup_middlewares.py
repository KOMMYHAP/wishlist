from logging import Logger

from telebot.async_telebot import AsyncTeleBot

from bot.middlewares.log_middleware import LoggerMiddleware
from bot.middlewares.migration_middleware import MigrationMiddleware
from bot.middlewares.user_state_middleware import StateAdapterMiddleware
from bot.middlewares.wish_middleware import WishMiddleware
from wish.state_adapters.state_base_adapter import StateBaseAdapter
from wish.wish_manager import WishManager


def setup_middlewares(bot: AsyncTeleBot, logger: Logger, state_adapter: StateBaseAdapter, wish_manager: WishManager):
    bot.setup_middleware(LoggerMiddleware(logger))
    bot.setup_middleware(StateAdapterMiddleware(state_adapter))
    bot.setup_middleware(WishMiddleware(wish_manager))
    bot.setup_middleware(MigrationMiddleware(wish_manager, logger, bot))
    pass
