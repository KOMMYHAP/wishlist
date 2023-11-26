from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from bot.filters.wishlist_viewer_filter import wishlist_viewer_callback_data
from bot.handlers.wish_viewer.wishlist_viewer import show_wishlist_viewer
from wish.wish_manager import WishManager


async def wishlist_viewer_query(call: CallbackQuery, bot: AsyncTeleBot, wish_manager: WishManager,
                                logger: Logger) -> None:
    logger = logger.getChild('wishlist_viewer')
    callback_data: dict = wishlist_viewer_callback_data.parse(callback_data=call.data)
    page_idx = int(callback_data['page_idx'])
    target_user_id = int(callback_data['target_user_id'])
    await bot.answer_callback_query(call.id)
    await show_wishlist_viewer(bot, call.message, target_user_id, wish_manager, logger, page_idx)
