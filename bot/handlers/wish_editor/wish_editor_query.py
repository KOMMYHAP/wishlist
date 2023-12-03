from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, Message

from bot.filters.wish_editor_query_filter import wish_editor_callback_data
from bot.handlers.wish_editor.wish_editor_draft import WishEditorDraft
from bot.keyboards.wish_edit_keyboard import make_wish_edit_keyboard
from bot.types.MessageArgs import MessageArgs
from wish.state_adapters.state_base_adapter import StateBaseAdapter
from wish.wish_manager import WishManager


async def wish_editor_query(call: CallbackQuery, bot: AsyncTeleBot,
                            wish_manager: WishManager, state: StateBaseAdapter, logger: Logger) -> None:
    logger = logger.getChild('wish_editor_query')

    callback_data: dict = wish_editor_callback_data.parse(callback_data=call.data)
    wish_id = int(callback_data['id'])
    should_create_new_wish = wish_id < 0

    await bot.answer_callback_query(call.id)
    wish_draft = await state.get_wish_editor_draft(call.from_user.id)

    if wish_draft and wish_draft.editor_id != call.message.id:
        await bot.reply_to(call.message, "Оки, давай отредактируем другое желание")
        await state.delete_wish_editor_draft(call.from_user.id)

    if should_create_new_wish:
        wish_draft = WishEditorDraft(call.message.id, '', '', '', None)
    else:
        wish = await wish_manager.get_wish(wish_id)
        if wish is None:
            logger.error('Trying to query editor for invalid wish id %d', wish_id)
            await bot.reply_to(call.message, 'Я не смог найти это желание, может попробуем с другим?')
            return
        wish_draft = WishEditorDraft(call.message.id, wish.title, wish.hint, wish.cost, wish.wish_id)

    await state.update_wish_editor_draft(call.from_user.id, wish_draft)

    await open_wish_editor_in_last_message(bot, call, logger, wish_manager, wish_draft)


async def open_wish_editor_in_last_message(bot: AsyncTeleBot, call: CallbackQuery, logger: Logger,
                                           wish_manager: WishManager, wish_draft: WishEditorDraft):
    args = await _open_wish_editor(wish_draft, wish_manager, call.from_user.id, logger)
    if args is None:
        await bot.send_message(call.message.chat.id, 'Что-то пошло не так, не мог бы ты попробовать снова?')
        return
    await bot.edit_message_text(args.text, call.message.chat.id, call.message.id, reply_markup=args.markup)


async def open_wish_editor_in_new_message(bot: AsyncTeleBot, message: Message, logger: Logger,
                                          wish_manager: WishManager, wish_draft: WishEditorDraft):
    args = await _open_wish_editor(wish_draft, wish_manager, message.from_user.id, logger)
    if args is None:
        await bot.reply_to(message, 'Что-то пошло не так, не мог бы ты попробовать снова?')
        return
    await bot.send_message(message.chat.id, args.text, reply_markup=args.markup)


async def _open_wish_editor(wish_draft: WishEditorDraft, wish_manager: WishManager,
                            owner_user_id: int, logger: Logger) -> MessageArgs | None:
    owner_user = await wish_manager.find_user_by_id(owner_user_id)
    if owner_user is None:
        logger.error("Cannot find user by id '%d'", owner_user_id)
        return None

    text = ""
    if len(wish_draft.title) > 0:
        text += f"\nНазвание: {wish_draft.title}"
    if len(wish_draft.hint) > 0:
        text += f"\nОписание: {wish_draft.hint}"
    if len(wish_draft.cost) > 0:
        text += f"\nСтоимость: {wish_draft.cost}"
    if len(text) == 0:
        text = "Создай новое желание:"

    return MessageArgs(text, make_wish_edit_keyboard(wish_draft))
