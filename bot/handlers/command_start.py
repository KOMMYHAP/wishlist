import datetime
from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import BotCommand, Message

from bot.handlers.command_registry import WishlistCommands, get_command_description
from bot.handlers.wish_editor.wishlist_editor import send_my_wishlist_editor
from wish.types.user import User, current_user_data_version
from wish.wish_manager import WishManager


async def command_start_handler(message: Message, bot: AsyncTeleBot, wish_manager: WishManager, logger: Logger) -> None:
    logger = logger.getChild('start_command')
    message_sender = message.from_user
    user = User(current_user_data_version, message_sender.id, message_sender.username, message_sender.first_name,
                message_sender.last_name, message.chat.id, datetime.datetime.fromtimestamp(0, datetime.UTC))

    bot_commands: list[BotCommand] = []
    for wishlist_command in WishlistCommands:
        bot_commands.append(
            BotCommand(command=wishlist_command.value, description=get_command_description(wishlist_command)))
    await bot.set_my_commands(bot_commands)

    new_user_created = await wish_manager.register_user(user)
    if new_user_created:
        hello_world_message = f"""Привет, {user.first_name} {user.last_name}!

Если тебя пригласили на день рождения и ты хочешь подарить именинику что-то действительно нужное, но не знаешь что, то я постараюсь тебе помочь!

Я могу показать тебе список желаний человека, а ты в свою очередь можешь рассказать мне свой, чтобы помочь другим людям выбрать и тебе качественный подарок.

ВНИМАНИЕ. 
Я НАХОЖУСЬ В АКТИВНОЙ РАЗРАБОТКЕ. 
БАГИ, ЗАВИСАНИЯ, НЕУДОБСТВА, ПОТЕРЯ ДАННЫХ - ВСЁ ЭТО МОИ ЛУЧШИЕ ДРУЗЬЯ.

Большое вам спасибо, что помогаете делать меня лучше.
Со всем пожеланиями, идеями, баг-репортами вы можете обращаться непосредственно к моему разработчику: @polyakov_white   
"""
        await bot.send_message(message.chat.id, hello_world_message)

    await send_my_wishlist_editor(logger, message, bot, wish_manager, 0)
