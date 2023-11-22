from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.filters.wish_edit_action_filter import wish_edit_action_callback_data
from bot.types.wish_edit_states import WishEditStates


def make_wish_edit_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    # todo: look at switch_inline_query_current_chat in InlineKeyboardButton

    keyboard.row(
        InlineKeyboardButton(
            text='Название',
            callback_data=wish_edit_action_callback_data.new(action=WishEditStates.TITLE.value)
        ),
        InlineKeyboardButton(
            text='Ссылки',
            callback_data=wish_edit_action_callback_data.new(action=WishEditStates.REFERENCES.value)
        ),
        InlineKeyboardButton(
            text='Отменить',
            callback_data=wish_edit_action_callback_data.new(action=WishEditStates.ABORT.value)
        ),
        InlineKeyboardButton(
            text='Применить',
            callback_data=wish_edit_action_callback_data.new(action=WishEditStates.COMPLETION.value)
        ),
    )
    return keyboard
