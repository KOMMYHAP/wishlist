from telebot import types
from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackDataFilter


class ButtonCallbackFilter(AdvancedCustomFilter):
    key = 'button'

    async def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
