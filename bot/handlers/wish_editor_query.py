from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, Message

from bot.filters.wish_editor_query_filter import wish_editor_callback_data
from bot.keyboards.wish_edit_keyboard import make_wish_edit_keyboard
from wish.state_adapters.state_base_adapter import StateBaseAdapter
from wish.types.wish_draft import WishDraft
from wish.wish_manager import WishManager


async def wish_editor_query(call: CallbackQuery, bot: AsyncTeleBot,
                            wish_manager: WishManager, state: StateBaseAdapter, logger: Logger) -> None:
    logger = logger.getChild('wish_editor_query')

    callback_data: dict = wish_editor_callback_data.parse(callback_data=call.data)
    wish_id = int(callback_data['id'])
    should_create_new_wish = wish_id < 0

    await bot.answer_callback_query(call.id)
    wish_draft = await state.get_wish_draft(call.from_user.id)

    if wish_draft and wish_draft.editor_id != call.message.id:
        await bot.reply_to(call.message, "Оки, давай отредактируем другое желание")
        await state.delete_wish_draft(call.from_user.id)

    if should_create_new_wish:
        wish_draft = WishDraft(call.message.id, '', '', 0.0, None)
    else:
        wish = await wish_manager.get_wish(call.from_user.id, wish_id)
        if wish is None:
            logger.error('Trying to query editor for invalid wish id %d', wish_id)
            await bot.reply_to(call.message, 'Я не смог найти это желание, может попробуем с другим?')
            return
        wish_draft = WishDraft(call.message.id, wish.title, wish.hint, wish.cost, wish.wish_id)

    await state.update_wish_draft(call.from_user.id, wish_draft)

    await open_wish_editor_in_last_message(call, bot, wish_draft)


async def open_wish_editor_in_last_message(call: CallbackQuery, bot: AsyncTeleBot, wish_draft: WishDraft):
    await _open_wish_editor(call.message.chat.id, call.message.id, False, bot, wish_draft)


async def open_wish_editor_in_new_message(message: Message, bot: AsyncTeleBot, wish_draft: WishDraft):
    await _open_wish_editor(message.chat.id, message.id, True, bot, wish_draft)


async def _open_wish_editor(chat_id: int, message_id: int, send_new_message: bool, bot: AsyncTeleBot,
                            wish_draft: WishDraft):
    title = wish_draft.title if len(wish_draft.title) > 0 else "<название отсутствует>"
    hint = wish_draft.hint if len(wish_draft.hint) > 0 else "<описание отсутствует>"
    cost = "{:.2f}".format(wish_draft.cost)
    text = f""""Редактор желания:
Название: {title}
Стоимость: {cost}
Описание: {hint}
"""

    if send_new_message:
        await bot.send_message(chat_id, text, reply_markup=make_wish_edit_keyboard(wish_draft.editor_id))
    else:
        await bot.edit_message_text(text, chat_id, message_id,
                                    reply_markup=make_wish_edit_keyboard(wish_draft.editor_id))
