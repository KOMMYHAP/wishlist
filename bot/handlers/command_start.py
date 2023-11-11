from typing import Awaitable, Any, Callable

from telebot import types
from telebot.async_telebot import AsyncTeleBot

from bot.keyboards.main_menu import generate_main_menu
from bot.types.button import Button


def init_start_command_handler(main_menu: dict[int, Button]) -> Callable[[Any], Awaitable]:
    async def start_command_handler_wrapped(message: types.Message, bot: AsyncTeleBot) -> None:
        await _start_command_handler(message, bot, main_menu)

    return start_command_handler_wrapped


async def _start_command_handler(message: types.Message, bot: AsyncTeleBot, main_menu: dict[int, Button]) -> None:
    await bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}",
                           reply_markup=generate_main_menu(main_menu))
