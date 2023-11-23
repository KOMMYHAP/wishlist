from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.types import CallbackQuery

wishlist_viewer_callback_data = CallbackData("page_idx", prefix="wishlist_viewer")


class WishlistViewerCallbackFilter(AdvancedCustomFilter):
    key = 'wishlist_viewer_config'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
