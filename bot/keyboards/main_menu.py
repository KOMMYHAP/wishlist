from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.types.button import Button


def generate_main_menu(main_menu_buttons: dict[int, Button]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    for button_id, button in main_menu_buttons.items():
        keyboard.add(InlineKeyboardButton(
            text=button.title,
            callback_data=Button.callback_factory().new(id=button_id)
        ))
    return keyboard
