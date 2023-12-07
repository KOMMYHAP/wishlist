from dataclasses import dataclass
from datetime import datetime

from wish.types.user import User


@dataclass
class FriendRecord:
    user: User
    request_counter: int
    last_access_time: datetime
    last_wishlist_edit_time: datetime
