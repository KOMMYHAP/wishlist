from telebot import types
from telebot.asyncio_filters import AdvancedCustomFilter


class WishStateFilter(AdvancedCustomFilter):
    def __init__(self, bot):
        self.bot = bot

    key = 'state'

    async def check(self, message, states):
        if states == '*':
            return True

        if isinstance(message, types.Message):
            chat_id = message.chat.id
            user_id = message.from_user.id
        elif isinstance(message, types.CallbackQuery):
            chat_id = message.message.chat.id
            user_id = message.from_user.id
        else:
            return False

        user_state = await self.bot.current_states.get_state(chat_id, user_id)
        if user_state == states:
            return True
        elif type(states) is list and user_state in states:
            return True

        return False
