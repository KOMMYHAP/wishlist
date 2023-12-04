from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.handlers.friends.friends_list import make_friends_list_args
from bot.handlers.wish_viewer.wish_viewer_states import WishViewerStates
from wish.wish_manager import WishManager


async def command_user_wishlist_handler(message: Message, bot: AsyncTeleBot, wish_manager: WishManager) -> None:
    user_id = message.from_user.id
    await bot.set_state(user_id, WishViewerStates.ASK_FOR_USERNAME.value)
    message_args = await make_friends_list_args(user_id, wish_manager)
    await bot.send_message(message.chat.id, message_args.text, reply_markup=message_args.markup)
