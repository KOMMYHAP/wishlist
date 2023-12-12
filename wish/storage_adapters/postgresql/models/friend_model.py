from datetime import datetime

from pydantic import BaseModel


class FriendModel(BaseModel):
    user_id: int
    friend_id: int
    request_counter: int
    access_time: datetime
    wishlist_seen_time: datetime
