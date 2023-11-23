from abc import ABC, abstractmethod

from wish.types.user import User
from wish.types.wish_record import WishRecord


class WishStorageBaseAdapter(ABC):
    @abstractmethod
    async def get_user_by_name(self, username: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User | None:
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
