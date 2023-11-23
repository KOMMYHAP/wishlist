from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message


async def wish_generic_message_handler(message: Message, bot: AsyncTeleBot, logger: Logger) -> None:
    logger = logger.getChild('wish_generic_message')
    logger.warning("Unknown message? User talks with bot? User's text: '%s'", message.text)
    await bot.reply_to(message, "Прости, кажется я тебя не понял.")
