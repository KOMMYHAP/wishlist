import datetime
from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.handlers.command_registry import WishlistCommands
from bot.handlers.wish_editor.wishlist_editor import send_my_wishlist_editor
from bot.handlers.wish_viewer.wishlist_viewer import send_user_wishlist_viewer
from bot.utilities.user_fullname import get_user_fullname
from bot.version import current_bot_version
from wish.types.user import User
from wish.wish_manager import WishManager


async def command_start_handler(message: Message, bot: AsyncTeleBot, wish_manager: WishManager, logger: Logger) -> None:
    logger = logger.getChild('start_command')
    message_sender = message.from_user

    _username = message_sender.username or ''
    _last_name = message_sender.last_name or ''
    user = User(current_bot_version, message_sender.id, _username, message_sender.first_name,
                _last_name, message.chat.id, datetime.datetime.fromtimestamp(0, datetime.UTC))

    new_user_created = await wish_manager.register_user(user)
    if new_user_created:
        hello_world_message = f"Привет, {get_user_fullname(user)}!\n\n{_start_message}"
        await bot.send_message(message.chat.id, hello_world_message)

    if len(message.text) > 0:
        await _command_start_with_deeplink(message, bot, wish_manager, logger)
    else:
        await send_my_wishlist_editor(logger, message, bot, wish_manager, 0)


async def _command_start_with_deeplink(message: Message, bot: AsyncTeleBot, wish_manager: WishManager,
                                       logger: Logger) -> None:
    target_user_id = _try_get_deep_linked_user_id(message.text)
    if target_user_id is None:
        await bot.reply_to(message, 'Некорректная ссылка! Попробуй попросить новую ссылку у твоего друга')
        return

    requested_user = await wish_manager.find_user_by_id(target_user_id)
    if not requested_user:
        await bot.reply_to(message,
                           'Я не смог найти вишлист этого человека! Попробуй попросить новую ссылку у твоего друга')
        return

    await send_user_wishlist_viewer(bot, logger, message, target_user_id, wish_manager, 0)


def _try_get_deep_linked_user_id(text: str) -> None | int:
    prefix = '/start '
    if not text.startswith(prefix):
        return None

    parameter = text.removeprefix(prefix)
    try:
        return int(parameter)
    except ValueError:
        return None


_start_message = f"""Если ты хочешь получить в подарок что-то действительно нужное...
Если тебя пригласили на день рождения, но ты не знаешь что подарить имениннику...
Если у человека вроде как всё есть и уже не осталось идей...

... то я постараюсь помочь тебе!  

Я могу показать тебе список желаний человека /{WishlistCommands.USER_WISHLIST.value}.
Ты можешь создать свой список желаний /{WishlistCommands.MY_WISHLIST.value}, чтобы помочь другим людям выбрать и тебе качественный подарок.
Также ты можешь следить за обновлением списка желаний своих друзей /{WishlistCommands.GET_UPDATES.value}.

Большое спасибо, что помогаешь делать меня лучше!
"""
