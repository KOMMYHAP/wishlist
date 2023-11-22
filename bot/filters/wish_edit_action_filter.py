from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackDataFilter, CallbackData
from telebot.types import CallbackQuery

wish_edit_action_callback_data = CallbackData("action", prefix="wish_edit")


class WishEditActionCallbackFilter(AdvancedCustomFilter):
    key = 'wish_edit_action_config'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
