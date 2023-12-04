from dataclasses import dataclass
from enum import Enum
from typing import Callable, Any

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class PageNavigation(Enum):
    BACK = 0,
    NEXT = 1


Item = Any

# Factory takes an item's index and object, e.g. (0, Item()), of existing wish or (-1, None) otherwise and returns a callback data for it.
ItemButtonFactory = Callable[[int, Any], InlineKeyboardButton]

# Factory takes an PageNavigation and index of page to redirect user and returns a callback data for it.
ItemPageCallbackDataFactory = Callable[[PageNavigation, int], InlineKeyboardButton]


@dataclass
class ListableMarkupParameters:
    current_page_idx: int
    items_per_page: int
    items: Item
    page_navigation_factory: ItemPageCallbackDataFactory
    item_button_factory: ItemButtonFactory


def _make_listable_markup(params: ListableMarkupParameters) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    items_range = range(params.current_page_idx * params.items_per_page,
                        (params.current_page_idx + 1) * params.items_per_page)
    for item_idx in items_range:
        if item_idx >= len(params.items):
            break

        item = params.items[item_idx]
        button = params.item_button_factory(item_idx, item)
        keyboard.row(button)

    last_page_idx = max(len(params.items) - 1, 0) // params.items_per_page

    back_page_idx = params.current_page_idx - 1
    if back_page_idx < 0:
        back_page_idx = last_page_idx

    next_page_idx = params.current_page_idx + 1
    if next_page_idx > last_page_idx:
        next_page_idx = 0

    back_button = params.page_navigation_factory(PageNavigation.BACK, back_page_idx)
    next_button = params.page_navigation_factory(PageNavigation.NEXT, next_page_idx)
    create_item_button = params.item_button_factory(-1, None)

    keyboard.row(back_button, create_item_button, next_button)
    return keyboard
