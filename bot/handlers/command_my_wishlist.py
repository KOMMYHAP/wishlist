from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.handlers.wishlist_get import show_wishlist
from wish.wish_manager import WishManager


async def command_my_wishlist_handler(message: Message, bot: AsyncTeleBot, wish_manager: WishManager) -> None:
    await show_wishlist(message.from_user, bot, wish_manager, 0)