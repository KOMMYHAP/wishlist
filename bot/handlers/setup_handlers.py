from telebot.async_telebot import AsyncTeleBot

from bot.filters.wish_edit_action_filter import wish_edit_action_callback_data
from bot.filters.wish_editor_query_filter import wish_editor_callback_data
from bot.handlers.command_start import start_command_handler
from bot.handlers.wish_edit_action_query import wish_edit_action_query
from bot.handlers.wish_edit_reference import wish_edit_reference_handler
from bot.handlers.wish_edit_title import wish_edit_title_handler
from bot.handlers.wish_editor_query import wish_editor_query
from bot.types.wish_edit_states import WishEditStates


def setup_handlers(bot: AsyncTeleBot):
    bot.register_message_handler(start_command_handler, commands=['start'], pass_bot=True)

    bot.register_callback_query_handler(wish_editor_query, None,
                                        wish_editor_query_config=wish_editor_callback_data.filter(), pass_bot=True)
    bot.register_callback_query_handler(wish_edit_action_query, None,
                                        wish_edit_action_config=wish_edit_action_callback_data.filter(), pass_bot=True)

    bot.register_message_handler(wish_edit_title_handler, pass_bot=True, state=WishEditStates.TITLE.value)
    bot.register_message_handler(wish_edit_reference_handler, pass_bot=True, state=WishEditStates.REFERENCES.value)
