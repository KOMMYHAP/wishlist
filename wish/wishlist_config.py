from dataclasses import dataclass


@dataclass
class WishlistConfig:
    wishes_per_page: int
    can_wish_owner_see_reservation: bool
