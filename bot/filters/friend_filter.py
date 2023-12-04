from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.types import CallbackQuery

friend_new_marker = -1
friend_callback_data = CallbackData("id", prefix="friend")
friends_list_callback_data = CallbackData("page_id", prefix="friends_list")
friend_action_callback_data = CallbackData("action_id", "friend_id", prefix="friend_action")


class FriendCallbackFilter(AdvancedCustomFilter):
    key = 'friend_config'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


class FriendsListCallbackFilter(AdvancedCustomFilter):
    key = 'friends_list_config'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
