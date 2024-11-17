from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.handlers.command_registry import WishlistCommands
from wish.types.user import User
from wish.wish_manager import WishManager


async def command_about_handler(message: Message, bot: AsyncTeleBot, logger: Logger, wish_manager: WishManager) -> None:
    logger = logger.getChild('about_command')
    message_sender = message.from_user

    user_id = message_sender.id
    user = await wish_manager.find_user_by_id(user_id)
    if user is None:
        logger.error('User "%d" was not registered!', user_id)
        return

    await bot.send_message(message.chat.id, _generate_about_message(user, wish_manager), disable_web_page_preview=True)


def _generate_share_link(user: User, wish_manager: WishManager) -> str:
    return f'https://t.me/{wish_manager.config.bot_username}?start={user.id}'


def _generate_about_message(user: User, wish_manager: WishManager) -> str:
    return f"""О боте:
/{WishlistCommands.MY_WISHLIST.value} — показать свой список желаний
/{WishlistCommands.USER_WISHLIST.value} — показать список желаний других пользователей
/{WishlistCommands.GET_UPDATES.value} — показать обновления желаний у других пользователей 
/{WishlistCommands.ABOUT.value} — показать данное сообщение

{_generate_share_link(user, wish_manager)} — поделиться своим списком желаний  
https://ko-fi.com/polyakov_white — купить автору кофе
https://t.me/polyakov_white — выразить благодарности автору
"""
