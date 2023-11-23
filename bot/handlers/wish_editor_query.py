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
        await bot.send_message(call.message.chat.id, "Оки, давай отредактируем другое желание")
        await state.delete_wish_draft(call.from_user.id)

    if should_create_new_wish:
        wish_draft = WishDraft(call.message.id, '', [], None)
    else:
        wish = await wish_manager.get_wish(call.from_user.id, wish_id)
        if wish is None:
            logger.error('Trying to query editor for invalid wish id %d', wish_id)
            raise NotImplementedError
        wish_draft = WishDraft(call.message.id, wish.title, wish.references, wish.wish_id)

    await state.update_wish_draft(call.from_user.id, wish_draft)

    await open_wish_editor_in_last_message(call, bot, state, logger)


async def open_wish_editor_in_last_message(call: CallbackQuery, bot: AsyncTeleBot,
                                           state: StateBaseAdapter, logger: Logger):
    await _open_wish_editor(call.message.chat.id, call.message.id, call.from_user.id,
                            False, bot, state, logger)


async def open_wish_editor_in_new_message(message: Message, bot: AsyncTeleBot,
                                          state: StateBaseAdapter, logger: Logger):
    await _open_wish_editor(message.chat.id, message.id, message.from_user.id, True, bot, state, logger)


async def _open_wish_editor(chat_id: int, message_id: int, user_id: int, send_new_message: bool, bot: AsyncTeleBot,
                            state: StateBaseAdapter,
                            logger: Logger):
    wish_draft = await state.get_wish_draft(user_id)
    if wish_draft is None:
        logger.error("Failed to open wish editor: wish draft not created!")
        raise NotImplementedError

    title = wish_draft.title if len(wish_draft.title) > 0 else "<нет названия>"
    references = '<нет ссылок>'
    if len(wish_draft.references) == 1:
        references = wish_draft.references[0]
    elif len(wish_draft.references) > 0:
        references = '\n - '.join(wish_draft.references)

    text = ("Редактор:\n"
            f"Название: {title}\n"
            f"Ссылка: {references}\n")

    if send_new_message:
        await bot.send_message(chat_id, text, reply_markup=make_wish_edit_keyboard(wish_draft.editor_id))
    else:
        await bot.edit_message_text(text, chat_id, message_id,
                                    reply_markup=make_wish_edit_keyboard(wish_draft.editor_id))
