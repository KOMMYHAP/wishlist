from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackDataFilter, CallbackData
from telebot.types import CallbackQuery

wish_editor_new_marker = -1
wish_editor_callback_data = CallbackData("id", prefix="wish_editor_query")


class WishEditorCallbackFilter(AdvancedCustomFilter):
    key = 'wish_editor_query_config'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
