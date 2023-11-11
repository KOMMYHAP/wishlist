from dataclasses import dataclass
from typing import Callable, Awaitable

from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.callback_data import CallbackData

from bot.types.button_context import ButtonContext


@dataclass
class Button:
    title: str
    callback: Callable[[types.CallbackQuery, AsyncTeleBot, ButtonContext], Awaitable[None]]

    @staticmethod
    def callback_factory() -> CallbackData:
        return CallbackData("id", prefix="button")
