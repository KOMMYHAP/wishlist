from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.filters.wish_view_action_filter import wish_view_action_callback_data
from bot.filters.wish_viewer_query_filter import wish_viewer_callback_data
from bot.handlers.wish_viewer.wish_viewer_draft import WishViewerDraft
from bot.handlers.wish_viewer.wish_viewer_states import WishViewerStates
from bot.utilities.user_fullname import get_user_fullname
from wish.state_adapters.state_base_adapter import StateBaseAdapter
from wish.types.wish_record import WishRecord
from wish.wish_manager import WishManager


async def wish_viewer_query(call: CallbackQuery, bot: AsyncTeleBot,
                            wish_manager: WishManager, state: StateBaseAdapter, logger: Logger) -> None:
    logger = logger.getChild('wish_viewer_query')

    callback_data: dict = wish_viewer_callback_data.parse(callback_data=call.data)
    wish_id = int(callback_data['id'])

    await bot.answer_callback_query(call.id)
    observer_id = call.from_user.id
    draft = await state.get_wish_viewer_draft(observer_id)

    if draft and draft.editor_id != call.message.id:
        await bot.reply_to(call.message, "Оки, давай отредактируем другое желание")
        await state.delete_wish_editor_draft(observer_id)

    wish = await wish_manager.get_wish(wish_id)
    if wish is None:
        logger.error('Trying to query viewer for invalid wish id %d', wish_id)
        await bot.reply_to(call.message, 'Я не смог найти это желание, может попробуем с другим?')
        return

    draft = WishViewerDraft(call.message.id, observer_id, wish.wish_id, False)

    await state.update_wish_viewer_draft(observer_id, draft)

    owner_user = await wish_manager.find_user_by_id(wish.owner_id)

    text = f"{get_user_fullname(owner_user, username=True)} хочет получить в подарок:"
    if len(wish.title) > 0:
        text += f"\nНазвание: {wish.title}"
    if len(wish.hint) > 0:
        text += f"\nОписание: {wish.hint}"
    if len(wish.cost) > 0:
        text += f"\nСтоимость: {wish.cost}"
    if wish.reserved_by_user_id is not None:
        reserved_by_user = await wish_manager.find_user_by_id(wish.reserved_by_user_id)
        if observer_id != wish.owner_id or wish_manager.config.allow_wish_owner_sees_reservation:
            text += f"\nХочет подарить: {get_user_fullname(reserved_by_user, username=True)}"
        else:
            text += f"\nКое-кто уже планирует подарить тебе этот подарок!"

    markup = _make_wish_view_markup(draft.editor_id, observer_id, wish)
    await bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=markup)


def _make_wish_view_markup(editor_id: int, observer_id: int, wish: WishRecord) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    if wish.reserved_by_user_id is None and wish.owner_id != observer_id:
        keyboard.row(InlineKeyboardButton(
            text='Планирую дарить',
            callback_data=wish_view_action_callback_data.new(action=WishViewerStates.RESERVATION.value,
                                                             editor_id=editor_id)
        ))
    elif wish.reserved_by_user_id is not None and observer_id == wish.reserved_by_user_id:
        keyboard.row(InlineKeyboardButton(
            text='Передумал дарить',
            callback_data=wish_view_action_callback_data.new(action=WishViewerStates.RESERVATION.value,
                                                             editor_id=editor_id)
        ))

    keyboard.row(
        InlineKeyboardButton(
            text='Вернуться',
            callback_data=wish_view_action_callback_data.new(action=WishViewerStates.BACK.value, editor_id=editor_id)
        ))
    return keyboard
