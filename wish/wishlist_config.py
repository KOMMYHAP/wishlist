from dataclasses import dataclass


@dataclass
class WishlistConfig:
    wishes_per_page: int
    allow_wish_owner_sees_reservation: bool
    allow_user_sees_owned_wishlist: bool
    initial_wish_id: int
    friends_count_on_page: int
    bot_username: str
