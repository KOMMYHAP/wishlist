import datetime
from enum import Enum

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.handlers.command_registry import WishlistCommands
from bot.handlers.friends.friends_list import make_friends_list_markup
from wish.types.friend_record import FriendRecord
from wish.wish_manager import WishManager


class FriendUpdateStatus(Enum):
    NO_FRIENDS = 0
    NO_UPDATES = 1
    UPDATES = 2


async def command_get_updates_handler(message: Message, bot: AsyncTeleBot, wish_manager: WishManager) -> None:
    user_id = message.from_user.id
    status, updates = await _get_updates(user_id, wish_manager)

    if status == FriendUpdateStatus.NO_FRIENDS:
        await bot.send_message(
            message.chat.id,
            "Скажи мне кто твои друзья и я проверю не придумали ли они что-то новенькое: "
            f"/{WishlistCommands.USER_WISHLIST.value}")
        return

    if status == FriendUpdateStatus.NO_UPDATES:
        await bot.send_message(message.chat.id, "Обновлений не найдено")
        return

    markup = make_friends_list_markup(updates, wish_manager.config.friends_count_on_page)
    await bot.send_message(message.chat.id, "Следующие пользователи обновили свой список желаний:", reply_markup=markup)


async def _get_updates(user_id: int, wish_manager: WishManager) -> (FriendUpdateStatus, list[FriendRecord]):
    friend_list = await wish_manager.get_friend_list(user_id)
    if len(friend_list) == 0:
        return FriendUpdateStatus.NO_FRIENDS, []

    updated_friend_records = []
    for friend_record in friend_list:
        if friend_record.user.wishlist_update_time == datetime.datetime.fromtimestamp(0, datetime.UTC):
            continue
        if friend_record.user.wishlist_update_time <= friend_record.last_wishlist_edit_time:
            continue
        updated_friend_records.append(friend_record)

    if len(updated_friend_records) == 0:
        return FriendUpdateStatus.NO_UPDATES, []

    return FriendUpdateStatus.UPDATES, updated_friend_records
