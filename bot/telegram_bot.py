#!/usr/bin/python
import argparse
from typing import Generator, Any

from telebot.async_telebot import AsyncTeleBot

from bot.handlers.button_add import button_add
from bot.handlers.button_edit import button_edit
from bot.handlers.button_generic_handler import init_button_handler
from bot.handlers.button_get import button_get
from bot.handlers.button_remove import button_remove
from bot.handlers.command_start import init_start_command_handler
from bot.types.button import Button
from bot.types.button_callback_filter import ButtonCallbackFilter
from bot.utilities.id_generator import id_generator
from wish.storage.storage_file import FileStorage
from wish.wish_manager import WishManager


def register_main_menu(unique_id_generator: Generator[int, Any, None]) -> dict[int, Button]:
    buttons: dict[int, Button] = {}
    buttons[next(unique_id_generator)] = Button('get', button_get)
    buttons[next(unique_id_generator)] = Button('add', button_add)
    buttons[next(unique_id_generator)] = Button('edit', button_edit)
    buttons[next(unique_id_generator)] = Button('remove', button_remove)
    return buttons


async def entry_point() -> None:
    parser = argparse.ArgumentParser("WishList telegram bot")
    parser.add_argument('-t', '--token', required=True)
    parser.add_argument('-f', '--storage-file', required=True)
    args = parser.parse_args()

    unique_id_generator = id_generator()
    main_menu_buttons = register_main_menu(unique_id_generator)

    bot = AsyncTeleBot(args.token)
    start_command_handler = init_start_command_handler(main_menu_buttons)
    bot.register_message_handler(start_command_handler, commands=['start'], pass_bot=True)

    bot.add_custom_filter(ButtonCallbackFilter())
    storage = FileStorage(args.storage_file)
    wish_manager = WishManager(storage)
    button_handler = init_button_handler(wish_manager, main_menu_buttons)
    bot.register_callback_query_handler(button_handler, None, button=Button.callback_factory().filter(), pass_bot=True)

    await bot.polling(non_stop=True)
