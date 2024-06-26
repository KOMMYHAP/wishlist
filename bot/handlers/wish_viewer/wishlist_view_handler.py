from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.handlers.bot_idle_state import bot_idle_state
from bot.handlers.friends.friends_list import update_friend_record_usage
from bot.handlers.wish_viewer.wishlist_viewer import send_user_wishlist_viewer
from bot.utilities.telegram_link import telegram_user_link
from wish.wish_manager import WishManager


async def wishlist_view_handler(message: Message, bot: AsyncTeleBot, wish_manager: WishManager, logger: Logger) -> None:
    logger = logger.getChild('wishlist_view_handler')
    await bot.set_state(message.from_user.id, bot_idle_state)

    username = message.text.strip()
    if len(username) == 0:
        await bot.reply_to(message, 'Имя пользователя должно иметь как минимум один видимый символ')
        return

    if username.startswith("@"):
        username = username.removeprefix("@")

    if username.startswith(telegram_user_link):
        username = username.removeprefix(telegram_user_link)

    target = await wish_manager.find_user_by_name(username)
    if target is None:
        await bot.reply_to(message, 'Я не смог найти такого пользователя')
        return

    await update_friend_record_usage(message.from_user.id, target.id, wish_manager)
    await send_user_wishlist_viewer(bot, logger, message, target.id, wish_manager, 0)
