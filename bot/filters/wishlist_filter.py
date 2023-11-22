from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.types import CallbackQuery

wishlist_callback_data = CallbackData("page_idx", prefix="wishlist")


class WishlistCallbackFilter(AdvancedCustomFilter):
    key = 'wishlist_config'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
