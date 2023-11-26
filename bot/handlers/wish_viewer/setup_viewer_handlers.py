from telebot.async_telebot import AsyncTeleBot

from bot.filters.wish_view_action_filter import wish_view_action_callback_data
from bot.filters.wish_viewer_query_filter import wish_viewer_callback_data
from bot.filters.wishlist_viewer_filter import wishlist_viewer_callback_data
from bot.handlers.command_registry import WishlistCommands
from bot.handlers.wish_viewer.command_user_wishlist import command_user_wishlist_handler
from bot.handlers.wish_viewer.wish_view_action_query import wish_view_action_query
from bot.handlers.wish_viewer.wish_viewer_query import wish_viewer_query
from bot.handlers.wish_viewer.wish_viewer_states import WishViewerStates
from bot.handlers.wish_viewer.wishlist_view_handler import wishlist_view_handler
from bot.handlers.wish_viewer.wishlist_viewer_query import wishlist_viewer_query


def setup_viewer_handlers(bot: AsyncTeleBot):
    bot.register_message_handler(command_user_wishlist_handler, commands=[WishlistCommands.USER_WISHLIST.value],
                                 pass_bot=True)

    # noinspection PyTypeChecker
    bot.register_callback_query_handler(wish_view_action_query, None,
                                        wish_view_action_config=wish_view_action_callback_data.filter(), pass_bot=True)
    # noinspection PyTypeChecker
    bot.register_callback_query_handler(wish_viewer_query, None,
                                        wish_viewer_query_config=wish_viewer_callback_data.filter(), pass_bot=True)
    # noinspection PyTypeChecker
    bot.register_callback_query_handler(wishlist_viewer_query, None,
                                        wishlist_viewer_config=wishlist_viewer_callback_data.filter(), pass_bot=True)

    bot.register_message_handler(wishlist_view_handler, pass_bot=True, state=WishViewerStates.ASK_FOR_USERNAME.value)
