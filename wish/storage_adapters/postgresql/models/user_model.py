from datetime import datetime

from pydantic import BaseModel


class UserModel(BaseModel):
    user_id: int
    user_name: str
    first_name: str
    last_name: str
    chat_id: int
    wishlist_update_time: datetime
    user_version: int
