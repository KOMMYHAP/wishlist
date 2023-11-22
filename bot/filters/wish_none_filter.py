from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.types import CallbackQuery

wish_blocked_callback_data = CallbackData("description", prefix="block")


class WishNoneCallbackFilter(AdvancedCustomFilter):
    key = 'wish_block_config'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
