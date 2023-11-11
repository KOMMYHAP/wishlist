from telebot import types
from telebot.async_telebot import AsyncTeleBot

from bot.types.button_context import ButtonContext


async def button_get(call: types.CallbackQuery, bot: AsyncTeleBot, context: ButtonContext) -> None:
    await bot.reply_to(call.message, f"Ты нажал на 'get'")
