from enum import Enum

from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.types import CallbackQuery

wish_creator_callback_data = CallbackData("title", "references", prefix="make_wish")


class WishCreatorCallbackFilter(AdvancedCustomFilter):
    key = 'wish_creator_config'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


class WishCreatorButtonAction(Enum):
    CHANGE_TITLE = 0,
    ADD_REFERENCES = 1
