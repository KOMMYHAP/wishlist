from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from bot.filters.wishlist_editor_filter import wishlist_editor_callback_data
from bot.handlers.wish_editor.wishlist_editor import edit_my_wishlist_editor
from wish.wish_manager import WishManager


async def wishlist_editor_query(call: CallbackQuery, bot: AsyncTeleBot, wish_manager: WishManager,
                                logger: Logger) -> None:
    logger = logger.getChild('wishlist_editor_query')
    callback_data: dict = wishlist_editor_callback_data.parse(callback_data=call.data)
    page_idx = int(callback_data['page_idx'])
    await bot.answer_callback_query(call.id)
    await edit_my_wishlist_editor(logger, call.message, bot, wish_manager, page_idx)
