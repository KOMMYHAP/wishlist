from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.handlers.wish_editor.wishlist_editor import send_my_wishlist_editor
from wish.wish_manager import WishManager


async def command_my_wishlist_handler(message: Message, bot: AsyncTeleBot, wish_manager: WishManager,
                                      logger: Logger) -> None:
    logger = logger.getChild('my_wishlist_command')
    await send_my_wishlist_editor(logger, message, bot, wish_manager, 0)
