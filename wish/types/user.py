from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    version: int
    id: int
    username: str
    first_name: str
    last_name: str
    chat_id: int
    wishlist_update_time: datetime
