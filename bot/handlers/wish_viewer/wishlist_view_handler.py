from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.handlers.wish_idle_state import wish_idle_state
from bot.handlers.wish_viewer.wishlist_viewer import show_wishlist_viewer
from wish.wish_manager import WishManager


async def wishlist_view_handler(message: Message, bot: AsyncTeleBot, wish_manager: WishManager, logger: Logger) -> None:
    logger = logger.getChild('wishlist_view_handler')
    await bot.set_state(message.from_user.id, wish_idle_state)

    username = message.text.strip()
    if len(username) == 0:
        await bot.reply_to(message, 'Имя пользователя должно иметь как минимум один видимый символ')
        return

    if username.startswith("@"):
        username = username.removeprefix("@")

    user_id = await wish_manager.find_user_id(username)
    if user_id is None:
        await bot.reply_to(message, 'Я не смог найти такого пользователя')
        return

    await show_wishlist_viewer(bot, message, user_id, wish_manager, logger, 0)
