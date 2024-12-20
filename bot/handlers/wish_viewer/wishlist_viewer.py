from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.callback_data import CallbackData
from telebot.types import Message, CallbackQuery

from bot.bot_types.message_args import MessageArgs
from bot.filters.wish_viewer_query_filter import wish_viewer_callback_data, wish_viewer_new_marker
from bot.filters.wishlist_viewer_filter import wishlist_viewer_callback_data
from bot.handlers.command_registry import WishlistCommands
from bot.handlers.wish_editor.wishlist_editor import send_my_wishlist_editor
from bot.handlers.wishlist_request import make_wishlist_request, WishlistRequestConfig
from wish.wish_manager import WishManager


async def send_user_wishlist_viewer(bot: AsyncTeleBot, logger: Logger, message: Message, target_user_id: int,
                                    wish_manager: WishManager,
                                    page_idx: int) -> None:
    if target_user_id == message.from_user.id and not wish_manager.config.allow_user_sees_owned_wishlist:
        await send_my_wishlist_editor(logger, message, bot, wish_manager, page_idx)
        return

    request = await _make_viewer_config(logger, wish_manager, message.from_user.id, target_user_id, page_idx)
    if request is None:
        await bot.reply_to(message, 'Что-то пошло не так, не мог бы ты попробовать снова?')
        return
    await bot.send_message(message.chat.id, request.text, reply_markup=request.markup)


async def edit_user_wishlist_viewer(bot: AsyncTeleBot, logger: Logger, call: CallbackQuery, target_user_id: int,
                                    wish_manager: WishManager,
                                    page_idx: int) -> None:
    if target_user_id == call.from_user.id and not wish_manager.config.allow_user_sees_owned_wishlist:
        await bot.send_message(call.message.chat.id,
                               f"Для просмотра личного списка желаний попробуй /{WishlistCommands.MY_WISHLIST.value}")
        return

    request = await _make_viewer_config(logger, wish_manager, call.from_user.id, target_user_id, page_idx)
    if request is None:
        await bot.send_message(call.message.chat.id, 'Что-то пошло не так, не мог бы ты попробовать снова?')
        return
    await bot.edit_message_text(request.text, call.message.chat.id, call.message.id, reply_markup=request.markup)


async def _make_viewer_config(logger: Logger, wish_manager: WishManager, sender_id: int, target_id: int,
                              current_page_idx: int) -> MessageArgs | None:
    sender = await wish_manager.find_user_by_id(sender_id)
    if sender is None:
        logger.error('Cannot find sender by id %d', sender_id)
        return
    target = await wish_manager.find_user_by_id(target_id)
    if target is None:
        logger.error('Cannot find target by id %d', sender_id)
        return

    def _page_navigation_factory(page_idx: int) -> CallbackData:
        return wishlist_viewer_callback_data.new(page_idx=page_idx, target_user_id=target.id)

    def _wish_factory(wish_idx: int | None) -> CallbackData:
        return wish_viewer_callback_data.new(id=wish_idx or wish_viewer_new_marker)

    config = WishlistRequestConfig(sender, target, current_page_idx,
                                   _page_navigation_factory,
                                   _wish_factory, False)
    request = await make_wishlist_request(config, wish_manager)
    if request is None:
        logger.error("Cannot find user's wishlist by user id %d", sender_id)
        return

    return request
