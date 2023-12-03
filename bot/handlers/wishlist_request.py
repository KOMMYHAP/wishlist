from dataclasses import dataclass
from typing import Callable

from telebot.callback_data import CallbackData
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from wish.types.user import User
from wish.types.wish_record import WishRecord
from wish.wish_manager import WishManager

# Factory takes an id of existing wish (int) or None otherwise and returns a callback data for it.
WishCallbackDataFactory = Callable[[int | None], CallbackData]

# Factory takes an index of page to redirect user and returns a callback data for it.
WishlistPageCallbackDataFactory = Callable[[int | None], CallbackData]


@dataclass
class WishlistRequestConfig:
    sender: User
    target: User
    current_page_idx: int
    page_navigation_factory: WishlistPageCallbackDataFactory
    wish_factory: WishCallbackDataFactory


@dataclass
class WishlistRequest:
    text: str
    reply_markup: InlineKeyboardMarkup


async def make_wishlist_request(config: WishlistRequestConfig, wish_manager: WishManager) -> WishlistRequest | None:
    wishes_per_page = wish_manager.wish_per_page
    response = await wish_manager.get_wishlist(config.sender.id, config.target.id)
    if response.owner is None or response.owner.id != config.target.id:
        return
    text = _make_wishlist_title(config, response.wishlist, wishes_per_page)
    markup = _make_wishlist_markup(config, response.wishlist, wishes_per_page)
    return WishlistRequest(text, markup)


def _make_wishlist_title(config: WishlistRequestConfig, wishlist: list[WishRecord], wishes_per_page: int) -> str:
    empty_wishlist = len(wishlist) == 0

    if config.sender.id != config.target.id:
        text = f"Список желаний от @{config.target.name}"
        if empty_wishlist:
            text += "\nПользователь еще не добавил желания"
    else:
        text = 'Мой список желаний'
        if empty_wishlist:
            text += "\nНажми '+', чтобы добавить желание."

    pages_count = len(wishlist) // wishes_per_page
    if pages_count > 1:
        text += f" (стр. {config.current_page_idx + 1}/{pages_count})"

    return text


def _make_wishlist_markup(config: WishlistRequestConfig, wishlist: list[WishRecord],
                          wishes_per_page: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    wish_id_range = range(config.current_page_idx * wishes_per_page, (config.current_page_idx + 1) * wishes_per_page)
    for wish_idx in wish_id_range:
        if wish_idx >= len(wishlist):
            break

        wish_record = wishlist[wish_idx]
        keyboard.row(InlineKeyboardButton(
            text=f"{wish_idx + 1}. {wish_record.title}",
            callback_data=config.wish_factory(wish_record.wish_id))
        )

    last_page_idx = max(len(wishlist) - 1, 0) // wishes_per_page

    back_page_idx = config.current_page_idx - 1
    if back_page_idx < 0:
        back_page_idx = last_page_idx

    next_page_idx = config.current_page_idx + 1
    if next_page_idx > last_page_idx:
        next_page_idx = 0

    back_callback = config.page_navigation_factory(back_page_idx)
    next_callback = config.page_navigation_factory(next_page_idx)
    create_wish_callback = config.wish_factory(None)

    keyboard.row(
        InlineKeyboardButton(text="←", callback_data=back_callback),
        InlineKeyboardButton(text="+", callback_data=create_wish_callback),
        InlineKeyboardButton(text=f"→", callback_data=next_callback)
    )

    return keyboard
