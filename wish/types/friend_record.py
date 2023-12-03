from dataclasses import dataclass

from wish.types.user import User


@dataclass
class FriendRecord:
    user: User
