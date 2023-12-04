from telebot.async_telebot import AsyncTeleBot

from bot.handlers.command_start import command_start_handler
from bot.handlers.friends.setup_friends_handlers import setup_friends_handlers
from bot.handlers.generic_message import generic_message_handler
from bot.handlers.wish_editor.setup_editor_handlers import setup_editor_handlers
from bot.handlers.wish_viewer.setup_viewer_handlers import setup_viewer_handlers


def setup_handlers(bot: AsyncTeleBot):
    bot.register_message_handler(command_start_handler, commands=['start'], pass_bot=True)

    setup_editor_handlers(bot)
    setup_viewer_handlers(bot)
    setup_friends_handlers(bot)

    # generic message handler should be the last handler due to its wildcard state
    bot.register_message_handler(generic_message_handler, pass_bot=True, state='*')
