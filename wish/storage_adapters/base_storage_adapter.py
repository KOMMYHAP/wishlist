from abc import ABC, abstractmethod

from wish.types.friend_record import FriendRecord
from wish.types.user import User
from wish.types.wish_record import WishRecord


class WishStorageBaseAdapter(ABC):
    @abstractmethod
    async def find_user_by_name(self, username: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def find_user_by_id(self, user_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def create_user(self, user: User) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def update_user(self, user: User) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_wishlist(self, user_id: int) -> list[WishRecord]:
        raise NotImplementedError

    @abstractmethod
    async def create_wish(self, wish: WishRecord) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_wish(self, wish_id: int) -> WishRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def update_wish(self, wish: WishRecord) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def remove_wish(self, user_id: int, wish_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_friend_list(self, user_id: int) -> list[FriendRecord]:
        raise NotImplementedError

    @abstractmethod
    async def remove_friend(self, user_id: int, friend_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def update_friend(self, user_id: int, friend_record: FriendRecord) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def create_friend(self, user_id: int, friend_record: FriendRecord) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def find_user_friend_by_id(self, user_id: int, friend_id: int) -> FriendRecord | None:
        raise NotImplementedError
