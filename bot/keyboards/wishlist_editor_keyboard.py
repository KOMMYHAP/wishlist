from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.filters.wish_editor_query_filter import wish_editor_callback_data, wish_editor_new_marker
from bot.filters.wishlist_filter import wishlist_callback_data
from wish.wish_manager import WishlistResponse


def generate_wishlist_editor_keyboard(wish_response: WishlistResponse, page_idx: int,
                                      wishes_per_page: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    first_page_idx = 0
    last_page_idx = (len(wish_response.wishlist) + wishes_per_page - 1) // wishes_per_page

    for wish_idx in range(page_idx * wishes_per_page, (page_idx + 1) * wishes_per_page):
        if wish_idx >= len(wish_response.wishlist):
            break

        wish_record = wish_response.wishlist[wish_idx]
        keyboard.row(InlineKeyboardButton(
            text=f"{wish_idx + 1}. {wish_record.title}",
            callback_data=wish_editor_callback_data.new(id=wish_record.wish_id))
        )

    back_callback = wishlist_callback_data.new(page_idx=last_page_idx if page_idx == first_page_idx else page_idx - 1)
    next_callback = wishlist_callback_data.new(page_idx=first_page_idx if page_idx == last_page_idx else page_idx + 1)
    create_wish_callback = wish_editor_callback_data.new(id=wish_editor_new_marker)

    keyboard.row(
        InlineKeyboardButton(text="←", callback_data=back_callback),
        InlineKeyboardButton(text="+", callback_data=create_wish_callback),
        InlineKeyboardButton(text=f"→", callback_data=next_callback)
    )

    return keyboard
