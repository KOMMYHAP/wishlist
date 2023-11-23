from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.handlers.wish_idle_state import wish_idle_state
from bot.handlers.wish_viewer.wishlist_viewer import show_wishlist_viewer
from wish.wish_manager import WishManager


async def wishlist_view_handler(message: Message, bot: AsyncTeleBot, wish_manager: WishManager, logger: Logger) -> None:
    logger = logger.getChild('wishlist_view_handler')

    username = message.text.strip()
    if len(username) <= 1 or not username.startswith('@'):
        await bot.reply_to(message, 'Имя пользователя должно начинаться с @ и иметь как минимум один видимый символ')
        return

    await bot.set_state(message.from_user.id, wish_idle_state)
    await show_wishlist_viewer(bot, message, username, wish_manager, logger, 0)
