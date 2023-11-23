from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.filters.wish_editor_query_filter import wish_editor_callback_data, wish_editor_new_marker
from bot.filters.wish_none_filter import wish_blocked_callback_data
from bot.filters.wishlist_filter import wishlist_callback_data
from wish.wish_manager import WishlistResponse


def generate_wishlist_keyboard(wishes: WishlistResponse, page_idx: int, wishes_per_page: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    back_navigation_restricted = page_idx == 0
    next_navigation_restricted = (page_idx + 1) * wishes_per_page > len(wishes.wishlist)

    for wish_idx in range(page_idx * wishes_per_page, (page_idx + 1) * wishes_per_page):
        if wish_idx >= len(wishes.wishlist):
            break

        wish_record = wishes.wishlist[wish_idx]
        keyboard.row(InlineKeyboardButton(
            text=f"#{wish_idx}. {wish_record.title}",
            callback_data=wish_editor_callback_data.new(id=wish_record.wish_id))
        )

    if back_navigation_restricted:
        back_callback = wish_blocked_callback_data.new(description="Нет доступных желаний")
    else:
        back_callback = wishlist_callback_data.new(page_idx=page_idx - 1)

    if next_navigation_restricted:
        next_callback = wish_blocked_callback_data.new(description="Нет доступных желаний")
    else:
        next_callback = wishlist_callback_data.new(page_idx=page_idx + 1)

    create_wish_callback = wish_editor_callback_data.new(id=wish_editor_new_marker)

    keyboard.row(
        InlineKeyboardButton(text="←", callback_data=back_callback),
        InlineKeyboardButton(text="+", callback_data=create_wish_callback),
        InlineKeyboardButton(text=f"→", callback_data=next_callback)
    )

    return keyboard
