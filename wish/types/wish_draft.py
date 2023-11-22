from dataclasses import dataclass
from enum import Enum

from bot.types.wish_edit_states import WishEditStates


@dataclass
class WishDraft:
    title: str
    references: list[str]
    wish_id: int | None
