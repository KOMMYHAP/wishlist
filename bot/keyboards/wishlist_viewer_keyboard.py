from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.filters.wish_viewer_query_filter import wish_viewer_callback_data
from bot.filters.wishlist_viewer_filter import wishlist_viewer_callback_data
from wish.wish_manager import WishlistResponse


def generate_wishlist_viewer_keyboard(wish_response: WishlistResponse, page_idx: int,
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
            callback_data=wish_viewer_callback_data.new(id=wish_record.wish_id))
        )

    back_callback = wishlist_viewer_callback_data.new(
        page_idx=last_page_idx if page_idx == first_page_idx else page_idx - 1)
    next_callback = wishlist_viewer_callback_data.new(
        page_idx=first_page_idx if page_idx == last_page_idx else page_idx + 1)

    keyboard.row(
        InlineKeyboardButton(text="←", callback_data=back_callback),
        InlineKeyboardButton(text=f"→", callback_data=next_callback)
    )

    return keyboard
