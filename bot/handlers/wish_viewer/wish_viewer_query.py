from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from bot.filters.wish_viewer_query_filter import wish_viewer_callback_data
from bot.handlers.wish_viewer.wish_viewer_draft import WishViewerDraft
from bot.keyboards.wish_view_keyboard import make_wish_view_keyboard
from wish.state_adapters.state_base_adapter import StateBaseAdapter
from wish.wish_manager import WishManager


async def wish_viewer_query(call: CallbackQuery, bot: AsyncTeleBot,
                            wish_manager: WishManager, state: StateBaseAdapter, logger: Logger) -> None:
    logger = logger.getChild('wish_viewer_query')

    callback_data: dict = wish_viewer_callback_data.parse(callback_data=call.data)
    wish_id = int(callback_data['id'])

    await bot.answer_callback_query(call.id)
    draft = await state.get_wish_viewer_draft(call.from_user.id)

    if draft and draft.editor_id != call.message.id:
        await bot.reply_to(call.message, "Оки, давай отредактируем другое желание")
        await state.delete_wish_editor_draft(call.from_user.id)

    wish = await wish_manager.get_wish(wish_id)
    if wish is None:
        logger.error('Trying to query viewer for invalid wish id %d', wish_id)
        await bot.reply_to(call.message, 'Я не смог найти это желание, может попробуем с другим?')
        return
    draft = WishViewerDraft(call.message.id, call.from_user.id, wish.wish_id, False)

    await state.update_wish_viewer_draft(call.from_user.id, draft)

    owner_username = await wish_manager.find_username(wish.owner_id)
    reserved_by_username = '<не зарезервировано>'
    if draft.reserved:
        reserved_by_username = call.from_user.username
    if wish.reserved_by_user_id is not None:
        reserved_by_username = await wish_manager.find_username(wish.reserved_by_user_id)

    title = wish.title if len(wish.title) > 0 else "<название отсутствует>"
    hint = wish.hint if len(wish.hint) > 0 else "<описание отсутствует>"
    cost = "{:.2f}".format(wish.cost)
    text = f"""Желание {owner_username}:
Название: {title}
Стоимость: {cost}
Описание: {hint}
Зарезервировано: {reserved_by_username}
"""

    await bot.edit_message_text(text, call.message.chat.id, call.message.id,
                                reply_markup=make_wish_view_keyboard(draft.editor_id))
