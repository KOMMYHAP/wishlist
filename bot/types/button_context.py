from dataclasses import dataclass

from wish.wish_manager import WishManager


@dataclass
class ButtonContext:
    wish_manager: WishManager
