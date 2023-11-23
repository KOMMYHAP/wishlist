from telebot.async_telebot import AsyncTeleBot

from bot.filters.wish_edit_action_filter import wish_edit_action_callback_data
from bot.filters.wish_editor_query_filter import wish_editor_callback_data
from bot.handlers.command_my_wishlist import command_my_wishlist_handler
from bot.handlers.command_registry import WishlistCommands
from bot.handlers.command_start import command_start_handler
from bot.handlers.wish_edit_action_query import wish_edit_action_query
from bot.handlers.wish_edit_cost import wish_edit_cost_handler
from bot.handlers.wish_edit_hint import wish_edit_hint_handler
from bot.handlers.wish_edit_title import wish_edit_title_handler
from bot.handlers.wish_editor_query import wish_editor_query
from bot.types.wish_edit_states import WishEditStates


def setup_handlers(bot: AsyncTeleBot):
    bot.register_message_handler(command_start_handler, commands=['start'], pass_bot=True)

    bot.register_message_handler(command_my_wishlist_handler, commands=[WishlistCommands.MY_WISHLIST.value],
                                 pass_bot=True)

    # noinspection PyTypeChecker
    bot.register_callback_query_handler(wish_editor_query, None,
                                        wish_editor_query_config=wish_editor_callback_data.filter(), pass_bot=True)

    # noinspection PyTypeChecker
    bot.register_callback_query_handler(wish_edit_action_query, None,
                                        wish_edit_action_config=wish_edit_action_callback_data.filter(), pass_bot=True)

    bot.register_message_handler(wish_edit_title_handler, pass_bot=True, state=WishEditStates.TITLE.value)
    bot.register_message_handler(wish_edit_cost_handler, pass_bot=True, state=WishEditStates.COST.value)
    bot.register_message_handler(wish_edit_hint_handler, pass_bot=True, state=WishEditStates.HINT.value)
