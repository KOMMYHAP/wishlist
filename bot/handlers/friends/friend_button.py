from enum import Enum
from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.filters.friend_filter import friend_callback_data, friend_action_callback_data
from bot.handlers.bot_idle_state import bot_idle_state
from bot.handlers.friends.friends_list import update_friend_record_usage, make_friends_list_args
from bot.handlers.wish_viewer.wishlist_viewer import edit_user_wishlist_viewer
from bot.utilities.user_fullname import get_user_fullname
from wish.wish_manager import WishManager


class FriendAction(Enum):
    SHOW_WISHLIST = 0
    DELETE = 1


async def friend_button_query(call: CallbackQuery, bot: AsyncTeleBot, wish_manager: WishManager,
                              logger: Logger) -> None:
    _ = logger.getChild('friend_button_query')
    await bot.set_state(call.message.from_user.id, bot_idle_state)
    await bot.answer_callback_query(call.id)

    callback_data: dict = friend_callback_data.parse(callback_data=call.data)
    friend_user_id = int(callback_data['id'])

    friend_user = await wish_manager.find_user_by_id(friend_user_id)
    if friend_user is None:
        await bot.send_message(call.message.chat.id, 'Что-то пошло не так, не мог бы ты попробовать снова?')
        return

    markup = _make_friend_action_markup(friend_user_id)
    fullname = get_user_fullname(friend_user, fullname=True, link=True)
    await bot.send_message(call.message.chat.id, f"Пользователь {fullname}", reply_markup=markup)


async def friend_action_query(call: CallbackQuery, bot: AsyncTeleBot, wish_manager: WishManager,
                              logger: Logger) -> None:
    _ = logger.getChild('friend_action_query')

    callback_data: dict = friend_action_callback_data.parse(callback_data=call.data)
    action_id = int(callback_data['action_id'])
    friend_user_id = int(callback_data['friend_id'])

    await bot.answer_callback_query(call.id)

    if action_id == FriendAction.SHOW_WISHLIST.value:
        await _friend_show_wishlist(bot, call, friend_user_id, logger, wish_manager)
    elif action_id == FriendAction.DELETE.value:
        await _remove_friend(bot, call, friend_user_id, wish_manager)


async def _remove_friend(bot: AsyncTeleBot, call: CallbackQuery, friend_user_id: int, wish_manager: WishManager):
    user_id = call.from_user.id
    friend_list = await wish_manager.get_friend_list(user_id)
    filtered_list = [x for x in friend_list if x.user.id != friend_user_id]
    await wish_manager.update_friend_list(user_id, filtered_list)
    message_args = await make_friends_list_args(user_id, wish_manager)
    await bot.send_message(call.message.chat.id, message_args.text, reply_markup=message_args.markup)


async def _friend_show_wishlist(bot: AsyncTeleBot, call: CallbackQuery, friend_user_id: int, logger: Logger,
                                wish_manager: WishManager) -> None:
    await update_friend_record_usage(call.from_user.id, friend_user_id, wish_manager)
    await edit_user_wishlist_viewer(bot, logger, call, friend_user_id, wish_manager, 0)


def _make_friend_action_markup(friend_user_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    button_show = InlineKeyboardButton(
        text='Список желаний',
        callback_data=friend_action_callback_data.new(action_id=FriendAction.SHOW_WISHLIST.value,
                                                      friend_id=friend_user_id)
    )
    button_delete = InlineKeyboardButton(
        text='Удалить',
        callback_data=friend_action_callback_data.new(action_id=FriendAction.DELETE.value,
                                                      friend_id=friend_user_id)
    )
    markup.add(button_show, button_delete, row_width=1)
    return markup
