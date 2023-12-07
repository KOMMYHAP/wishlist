from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.filters.wish_edit_action_filter import wish_edit_action_callback_data
from bot.handlers.wish_editor.wish_editor_draft import WishEditorDraft
from bot.types.wish_edit_states import WishEditStates


def make_wish_edit_keyboard(wish_draft: WishEditorDraft) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton(
            text='Название',
            callback_data=wish_edit_action_callback_data.new(action=WishEditStates.TITLE.value,
                                                             editor_id=wish_draft.editor_id)
        ),
        InlineKeyboardButton(
            text='Описание',
            callback_data=wish_edit_action_callback_data.new(action=WishEditStates.HINT.value,
                                                             editor_id=wish_draft.editor_id)
        ),
        InlineKeyboardButton(
            text='Стоимость',
            callback_data=wish_edit_action_callback_data.new(action=WishEditStates.COST.value,
                                                             editor_id=wish_draft.editor_id)
        )
    )

    if wish_draft.wish_id is not None:
        keyboard.row(
            InlineKeyboardButton(
                text='Удалить',
                callback_data=wish_edit_action_callback_data.new(action=WishEditStates.DELETE.value,
                                                                 editor_id=wish_draft.editor_id)
            ))

    keyboard.row(
        InlineKeyboardButton(
            text='Отменить',
            callback_data=wish_edit_action_callback_data.new(action=WishEditStates.ABORT.value,
                                                             editor_id=wish_draft.editor_id)
        ),
        InlineKeyboardButton(
            text='Применить',
            callback_data=wish_edit_action_callback_data.new(action=WishEditStates.COMPLETION.value,
                                                             editor_id=wish_draft.editor_id)
        )
    )
    return keyboard
