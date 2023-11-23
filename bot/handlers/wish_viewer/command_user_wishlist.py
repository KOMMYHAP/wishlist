from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.handlers.wish_viewer.wish_viewer_states import WishViewerStates


async def command_user_wishlist_handler(message: Message, bot: AsyncTeleBot) -> None:
    await bot.set_state(message.from_user.id, WishViewerStates.ASK_FOR_USERNAME.value)
    await bot.send_message(message.chat.id, "Введи имя пользователя")
