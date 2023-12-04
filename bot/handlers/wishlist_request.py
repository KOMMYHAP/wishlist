from dataclasses import dataclass
from typing import Callable

from telebot.callback_data import CallbackData
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.handlers.listable_markup import _make_listable_markup, ListableMarkupParameters, PageNavigation
from bot.types.MessageArgs import MessageArgs
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


async def make_wishlist_request(config: WishlistRequestConfig, wish_manager: WishManager) -> MessageArgs | None:
    wishes_per_page = wish_manager.config.wishes_per_page
    response = await wish_manager.get_wishlist(config.sender.id, config.target.id)
    if response.owner is None or response.owner.id != config.target.id:
        return
    text = _make_wishlist_title(config, response.wishlist, wishes_per_page)
    markup = _make_wishlist_markup(config, response.wishlist, wishes_per_page)
    return MessageArgs(text, markup)


def _make_wishlist_title(config: WishlistRequestConfig, wishlist: list[WishRecord], wishes_per_page: int) -> str:
    empty_wishlist = len(wishlist) == 0

    if config.sender.id != config.target.id:
        text = f"Список желаний от @{config.target.username}"
        if empty_wishlist:
            text += "\nПользователь еще не добавил желания"
    else:
        text = 'Мой список желаний'
        if empty_wishlist:
            text += "\nНажми '+', чтобы добавить желание."

    pages_count = (len(wishlist) + wishes_per_page - 1) // wishes_per_page
    if pages_count > 1:
        text += f" (стр. {config.current_page_idx + 1}/{pages_count})"

    return text


def _make_wishlist_markup(config: WishlistRequestConfig, wishlist: list[WishRecord],
                          wishes_per_page: int) -> InlineKeyboardMarkup:
    def _wish_navigation_button_factory(navigation: PageNavigation, page_idx: int) -> InlineKeyboardButton:
        navigation_text = "←" if navigation == PageNavigation.BACK else ""
        return InlineKeyboardButton(text=navigation_text, callback_data=config.page_navigation_factory(page_idx))

    def _wish_button_factory(wish_idx: int, wish: WishRecord) -> InlineKeyboardButton:
        if wish is None:
            InlineKeyboardButton(text="+", callback_data=config.wish_factory(None))

        return InlineKeyboardButton(
            text=f"{wish_idx + 1}. {wish.title}",
            callback_data=config.wish_factory(wish.wish_id))

    params = ListableMarkupParameters(
        config.current_page_idx,
        wishes_per_page,
        wishlist,
        _wish_navigation_button_factory,
        _wish_button_factory,
    )
    return _make_listable_markup(params)
