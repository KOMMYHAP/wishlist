from typing import Awaitable, Any, Callable

from telebot import types
from telebot.async_telebot import AsyncTeleBot

from bot.handlers.wishlist_get import show_wishlist
from wish.types.user import User
from wish.wish_manager import WishManager


def make_start_command_handler(wish_manager: WishManager) -> Callable[[Any], Awaitable]:
    async def start_command_handler_wrapped(message: types.Message, bot: AsyncTeleBot) -> None:
        await start_command_handler(message, bot, wish_manager)

    return start_command_handler_wrapped


async def start_command_handler(message: types.Message, bot: AsyncTeleBot, wish_manager: WishManager) -> None:
    user = User(message.from_user.id, message.from_user.username)
    new_user_created = await wish_manager.register_user(user)
    if new_user_created:
        await bot.send_message(message.chat.id, f'Привет, {user.name}!')
    await show_wishlist(message.from_user, bot, wish_manager, None)
