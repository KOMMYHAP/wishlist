from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.callback_data import CallbackData
from telebot.types import Message

from bot.filters.wish_editor_query_filter import wish_editor_callback_data, wish_editor_new_marker
from bot.filters.wishlist_editor_filter import wishlist_editor_callback_data
from bot.handlers.wishlist_request import make_wishlist_request, WishlistRequestConfig, WishlistRequest
from wish.wish_manager import WishManager


async def send_my_wishlist_editor(logger: Logger, message: Message, bot: AsyncTeleBot, wish_manager: WishManager,
                                  page_idx: int) -> None:
    request = await _make_editor_config(logger, wish_manager, message.from_user.id, page_idx)
    if request is None:
        await bot.reply_to(message, 'Что-то пошло не так, не мог бы ты попробовать снова?')
        return
    await bot.send_message(message.chat.id, request.text, reply_markup=request.reply_markup)


async def edit_my_wishlist_editor(logger: Logger, message: Message, bot: AsyncTeleBot, wish_manager: WishManager,
                                  page_idx: int) -> None:
    request = await _make_editor_config(logger, wish_manager, message.from_user.id, page_idx)
    if request is None:
        await bot.reply_to(message, 'Что-то пошло не так, не мог бы ты попробовать снова?')
        return
    await bot.edit_message_text(request.text, message.id, reply_markup=request.reply_markup)


def _my_wishlist_page_navigation_factory(page_idx: int) -> CallbackData:
    return wishlist_editor_callback_data.new(page_idx=page_idx)


def _wish_editor_callback_factory(wish_idx: int | None) -> CallbackData:
    return wish_editor_callback_data.new(id=wish_idx or wish_editor_new_marker)


async def _make_editor_config(logger: Logger, wish_manager: WishManager, sender_id: int,
                              page_idx: int) -> WishlistRequest | None:
    sender = await wish_manager.find_user_by_id(sender_id)
    if sender is None:
        logger.error('Cannot find user by id %d', sender_id)
        return

    config = WishlistRequestConfig(sender, sender, page_idx,
                                   _my_wishlist_page_navigation_factory,
                                   _wish_editor_callback_factory)
    request = await make_wishlist_request(config, wish_manager)
    if request is None:
        logger.error("Cannot find user's wishlist by user id %d", sender_id)
        return

    return request
