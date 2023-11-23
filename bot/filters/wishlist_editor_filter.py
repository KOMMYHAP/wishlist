from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.types import CallbackQuery

wishlist_editor_callback_data = CallbackData("page_idx", prefix="wishlist_editor")


class WishlistEditorCallbackFilter(AdvancedCustomFilter):
    key = 'wishlist_editor_config'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
