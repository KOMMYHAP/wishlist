from dataclasses import dataclass

from telebot.types import InlineKeyboardMarkup


@dataclass
class MessageArgs:
    text: str
    markup: InlineKeyboardMarkup | None
