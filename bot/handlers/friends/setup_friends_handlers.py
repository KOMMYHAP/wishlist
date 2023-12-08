from telebot.async_telebot import AsyncTeleBot

from bot.filters.friend_filter import friend_callback_data, friend_action_callback_data, friends_list_callback_data
from bot.handlers.command_registry import WishlistCommands
from bot.handlers.friends.friend_button import friend_button_query, friend_action_query
from bot.handlers.friends.friends_list import friends_list_navigation_query
from bot.handlers.friends.friends_updates import command_get_updates_handler


def setup_friends_handlers(bot: AsyncTeleBot):
    bot.register_message_handler(command_get_updates_handler, commands=[WishlistCommands.GET_UPDATES.value],
                                 pass_bot=True)

    # noinspection PyTypeChecker
    bot.register_callback_query_handler(friend_button_query, None,
                                        friend_config=friend_callback_data.filter(), pass_bot=True)

    # noinspection PyTypeChecker
    bot.register_callback_query_handler(friend_action_query, None,
                                        friend_config=friend_action_callback_data.filter(), pass_bot=True)
    # noinspection PyTypeChecker
    bot.register_callback_query_handler(friends_list_navigation_query, None,
                                        friend_config=friends_list_callback_data.filter(), pass_bot=True)
