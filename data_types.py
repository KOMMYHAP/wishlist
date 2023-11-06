from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str


@dataclass
class WishlistRecord:
    wish_id: int
    user_id: int
    title: str
    references: list[str]
    reserved_by_user: int | None
    performed: bool
