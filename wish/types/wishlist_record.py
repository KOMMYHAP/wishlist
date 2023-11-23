from dataclasses import dataclass


@dataclass
class WishlistRecord:
    wish_id: int
    owner_id: int  # same as User.id
    title: str
    hint: str
    cost: float
    reserved_by_user_id: int | None  # same as User.id
    performed: bool  # wish was performed by owner
