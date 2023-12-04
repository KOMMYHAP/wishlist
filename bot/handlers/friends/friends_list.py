import datetime
from enum import Enum

from telebot.types import InlineKeyboardButton

from bot.filters.friend_filter import friend_callback_data, friends_list_callback_data, friend_new_marker
from bot.handlers.listable_markup import PageNavigation, _make_listable_markup, ListableMarkupParameters
from bot.types.MessageArgs import MessageArgs
from bot.utilities.user_fullname import get_user_fullname
from wish.types.friend_record import FriendRecord
from wish.wish_manager import WishManager


async def make_friends_list_args(user_id: int, wish_manager: WishManager) -> MessageArgs:
    friends_list = await wish_manager.get_friend_list(user_id)
    if len(friends_list) == 0:
        return MessageArgs('Введи имя пользователя или ссылку на него', None)

    friends_list_by_access_time = sorted(friends_list, key=lambda r: r.last_access_time, reverse=True)

    def _friend_navigation_button_factory(navigation: PageNavigation, page_idx: int) -> InlineKeyboardButton:
        navigation_text = "←" if navigation == PageNavigation.BACK else ""
        return InlineKeyboardButton(text=navigation_text, callback_data=friends_list_callback_data.new(page_idx))

    def _friend_button_factory(_: int, friend: FriendRecord | None) -> InlineKeyboardButton:
        if friend is None:
            InlineKeyboardButton(text="+", callback_data=friend_callback_data.new(id=friend_new_marker))

        return InlineKeyboardButton(
            text=get_user_fullname(friend.user),
            callback_data=friend_callback_data.new(id=friend.user.id))

    params = ListableMarkupParameters(
        0,
        wish_manager.config.friends_count_on_page,
        friends_list_by_access_time,
        _friend_navigation_button_factory,
        _friend_button_factory
    )

    markup = _make_listable_markup(params)
    return MessageArgs('Введи имя пользователя или выбери из списка недавних:', markup)


class FriendDataUpdateResult(Enum):
    ADDED = 0,
    FOUND = 1,
    UNKNOWN_USER = 2


async def update_friend_record_usage(user_id: int, friend_user_id: int,
                                     wish_manager: WishManager) -> FriendDataUpdateResult:
    user = await wish_manager.find_user_by_id(friend_user_id)
    if user is None:
        return FriendDataUpdateResult.UNKNOWN_USER

    friends_list = await wish_manager.get_friend_list(user_id)
    found_friend_record = None
    for friend_record in friends_list:
        if friend_record.user.id == friend_user_id:
            break
        found_friend_record = friend_record

    now = datetime.datetime.now(datetime.UTC)

    if found_friend_record is not None:
        found_friend_record.request_counter += 1
        found_friend_record.last_access_time = now
    else:
        new_friend_record = FriendRecord(user, 0, now)
        friends_list.append(new_friend_record)

    await wish_manager.update_friend_list(user_id, friends_list)

    return FriendDataUpdateResult.ADDED
