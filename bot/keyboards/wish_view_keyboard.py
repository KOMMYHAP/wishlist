from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.filters.wish_view_action_filter import wish_view_action_callback_data
from bot.handlers.wish_viewer.wish_viewer_states import WishViewerStates


def make_wish_view_keyboard(editor_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            text='Зарезервировать',
            callback_data=wish_view_action_callback_data.new(action=WishViewerStates.RESERVATION.value,
                                                             editor_id=editor_id)
        ),
        InlineKeyboardButton(
            text='Вернуться',
            callback_data=wish_view_action_callback_data.new(action=WishViewerStates.BACK.value, editor_id=editor_id)
        ),
        row_width=1
    )
    return keyboard
