from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message


async def generic_message_handler(message: Message, bot: AsyncTeleBot, logger: Logger) -> None:
    logger = logger.getChild('wish_generic_message')
    if message.text == "ping":
        await bot.reply_to(message, "pong")

    logger.warning("Unknown message? User talks with bot? User's text: '%s'", message.text)
    await bot.reply_to(message, "Прости, кажется я тебя не понял.")
