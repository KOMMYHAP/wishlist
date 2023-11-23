from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.filters.wish_edit_action_filter import wish_edit_action_callback_data
from bot.types.wish_edit_states import WishEditStates


def make_wish_edit_keyboard(editor_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    # todo: look at switch_inline_query_current_chat in InlineKeyboardButton

    keyboard.row(
        InlineKeyboardButton(
            text='Название',
            callback_data=wish_edit_action_callback_data.new(action=WishEditStates.TITLE.value, editor_id=editor_id)
        ),
        InlineKeyboardButton(
            text='Описание',
            callback_data=wish_edit_action_callback_data.new(action=WishEditStates.HINT.value,
                                                             editor_id=editor_id)
        )
    )

    keyboard.row(
        InlineKeyboardButton(
            text='Стоимость',
            callback_data=wish_edit_action_callback_data.new(action=WishEditStates.COST.value, editor_id=editor_id)
        ),
        InlineKeyboardButton(
            text='Ссылки',
            callback_data=wish_edit_action_callback_data.new(action=WishEditStates.REFERENCES.value,
                                                             editor_id=editor_id)
        )
    )

    keyboard.row(
        InlineKeyboardButton(
            text='Отменить',
            callback_data=wish_edit_action_callback_data.new(action=WishEditStates.ABORT.value, editor_id=editor_id)
        ),
        InlineKeyboardButton(
            text='Применить',
            callback_data=wish_edit_action_callback_data.new(action=WishEditStates.COMPLETION.value,
                                                             editor_id=editor_id)
        )
    )
    return keyboard
