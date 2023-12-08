import datetime
from enum import Enum

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.filters.friend_filter import friend_callback_data, friends_list_callback_data
from bot.handlers.listable_markup import PageNavigation, _make_listable_markup, ListableMarkupParameters
from bot.types.MessageArgs import MessageArgs
from bot.utilities.suite_symbols import SuiteSymbols
from bot.utilities.user_fullname import get_user_fullname
from wish.types.friend_record import FriendRecord
from wish.wish_manager import WishManager


def make_friends_list_markup(friends_list: list[FriendRecord],
                             friends_count_on_page: int) -> InlineKeyboardMarkup | None:
    if len(friends_list) == 0:
        return None

    friends_list_by_access_time = sorted(friends_list, key=lambda r: r.last_access_time)

    def _friend_navigation_button_factory(navigation: PageNavigation, page_idx: int) -> InlineKeyboardButton:
        navigation_text = SuiteSymbols.ARROW_LEFT.value if navigation == PageNavigation.BACK else SuiteSymbols.ARROW_RIGHT.value
        return InlineKeyboardButton(text=navigation_text, callback_data=friends_list_callback_data.new(page_idx))

    def _friend_button_factory(_: int, friend: FriendRecord | None) -> InlineKeyboardButton | None:
        if friend is None:
            return None

        return InlineKeyboardButton(
            text=get_user_fullname(friend.user, username=True),
            callback_data=friend_callback_data.new(id=friend.user.id))

    params = ListableMarkupParameters(
        0,
        friends_count_on_page,
        friends_list_by_access_time,
        _friend_navigation_button_factory,
        _friend_button_factory
    )

    return _make_listable_markup(params)


async def make_friends_list_args(user_id: int, wish_manager: WishManager) -> MessageArgs:
    friends_list = await wish_manager.get_friend_list(user_id)
    markup = make_friends_list_markup(friends_list, wish_manager.config.wishes_per_page)
    if markup is None:
        return MessageArgs('Введи имя пользователя или ссылку на него', None)
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
            found_friend_record = friend_record
            break

    now = datetime.datetime.now(datetime.UTC)
    zero = datetime.datetime.fromtimestamp(0, datetime.UTC)

    if found_friend_record is not None:
        found_friend_record.request_counter += 1
        found_friend_record.last_access_time = now
        found_friend_record.last_wishlist_edit_time = user.wishlist_update_time
    else:
        new_friend_record = FriendRecord(user, 1, now, zero)
        friends_list.append(new_friend_record)

    await wish_manager.update_friend_list(user_id, friends_list)

    return FriendDataUpdateResult.ADDED
