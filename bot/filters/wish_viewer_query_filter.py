from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackDataFilter, CallbackData
from telebot.types import CallbackQuery

wish_viewer_callback_data = CallbackData("id", prefix="wish_viewer_query")


class WishViewerCallbackFilter(AdvancedCustomFilter):
    key = 'wish_viewer_query_config'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
