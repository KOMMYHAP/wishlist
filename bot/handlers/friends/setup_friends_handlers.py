from telebot.async_telebot import AsyncTeleBot

from bot.filters.friend_filter import friend_callback_data, friend_action_callback_data
from bot.handlers.friends.friend_button import friend_button_query, friend_action_query


def setup_friends_handlers(bot: AsyncTeleBot):
    # noinspection PyTypeChecker
    bot.register_callback_query_handler(friend_button_query, None,
                                        friend_config=friend_callback_data.filter(), pass_bot=True)

    # noinspection PyTypeChecker
    bot.register_callback_query_handler(friend_action_query, None,
                                        friend_config=friend_action_callback_data.filter(), pass_bot=True)
