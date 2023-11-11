import logging
from typing import Awaitable, Any, Callable

from telebot import types
from telebot.async_telebot import AsyncTeleBot

from bot.types.button import Button
from bot.types.button_context import ButtonContext
from wish.wish_manager import WishManager


def init_button_handler(wish_manager: WishManager, button_map: dict[int, Button]) -> Callable[[Any], Awaitable]:
    context = ButtonContext(wish_manager)
    logger = logging.getLogger('generic_button_handler')

    async def _button_handler_wrapped(call: types.CallbackQuery, bot: AsyncTeleBot) -> None:
        await _button_handler(call, bot, context, logger, button_map)

    return _button_handler_wrapped


async def _button_handler(call: types.CallbackQuery,
                          bot: AsyncTeleBot,
                          button_context: ButtonContext,
                          logger: logging.Logger,
                          button_map: dict[int, Button]) -> None:
    callback_data: dict = Button.callback_factory().parse(callback_data=call.data)
    button_id = int(callback_data['id'])
    button: Button | None = button_map.get(button_id)
    if button is None:
        logger.error('Button with id %d was not registered!', button_id)
        return

    await button.callback(call, bot, button_context)
    await bot.answer_callback_query(call.id)
