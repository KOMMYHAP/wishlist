from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message


async def command_about_handler(message: Message, bot: AsyncTeleBot, logger: Logger) -> None:
    logger = logger.getChild('about_command')
    message_sender = message.from_user

    username = message_sender.username or ''
    user_id = message_sender.id
    logger.info('User "%s" (id: %s) wants to know more about me!', username, user_id)

    await bot.send_message(message.chat.id, _about_message)


_about_message = f"""Данный бот изначально являлся домашним проектом для автора и его узкого круга друзей, однако перерос в нечто большее.
И сейчас это нечто требует время разработчика на поддержку сервера, исправление проблем и добавление нового функционала :) 

Ваши пожелания, идеи и баг-репорты приветствуются здесь: @polyakov_white.
А благодарности здесь: +79994638280, https://ko-fi.com/polyakov_white.

Спасибо!
"""
