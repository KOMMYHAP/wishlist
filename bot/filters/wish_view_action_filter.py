from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackDataFilter, CallbackData
from telebot.types import CallbackQuery

wish_view_action_callback_data = CallbackData("action", "editor_id", prefix="wish_view")


class WishViewActionCallbackFilter(AdvancedCustomFilter):
    key = 'wish_view_action_config'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
