from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.handlers.wish_idle_state import wish_idle_state
from bot.handlers.wish_viewer.wishlist_viewer import send_user_wishlist_viewer
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

    target = await wish_manager.find_user_by_name(username)
    if target is None:
        await bot.reply_to(message, 'Я не смог найти такого пользователя')
        return
    await send_user_wishlist_viewer(bot, logger, message, target.id, wish_manager, 0)
