from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.filters.wish_editor_query_filter import wish_editor_callback_data, wish_editor_new_marker
from bot.filters.wishlist_editor_filter import wishlist_editor_callback_data
from wish.wish_manager import WishlistResponse


def generate_wishlist_editor_keyboard(wish_response: WishlistResponse, page_idx: int,
                                      wishes_per_page: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    for wish_idx in range(page_idx * wishes_per_page, (page_idx + 1) * wishes_per_page):
        if wish_idx >= len(wish_response.wishlist):
            break

        wish_record = wish_response.wishlist[wish_idx]
        keyboard.row(InlineKeyboardButton(
            text=f"{wish_idx + 1}. {wish_record.title}",
            callback_data=wish_editor_callback_data.new(id=wish_record.wish_id))
        )

    last_page_idx = max(len(wish_response.wishlist) - 1, 0) // wishes_per_page

    back_page_idx = page_idx - 1
    if back_page_idx < 0:
        back_page_idx = last_page_idx

    next_page_idx = page_idx + 1
    if next_page_idx > last_page_idx:
        next_page_idx = 0

    back_callback = wishlist_editor_callback_data.new(page_idx=back_page_idx)
    next_callback = wishlist_editor_callback_data.new(page_idx=next_page_idx)
    create_wish_callback = wish_editor_callback_data.new(id=wish_editor_new_marker)

    keyboard.row(
        InlineKeyboardButton(text="←", callback_data=back_callback),
        InlineKeyboardButton(text="+", callback_data=create_wish_callback),
        InlineKeyboardButton(text=f"→", callback_data=next_callback)
    )

    return keyboard
