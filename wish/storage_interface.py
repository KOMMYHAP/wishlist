from abc import ABC, abstractmethod

from wish.data_types import User, WishlistRecord


class BaseStorage(ABC):
    @abstractmethod
    async def get_user_by_name(self, username: str) -> User | None:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def create_user(self, user: User) -> bool:
        pass

    @abstractmethod
    async def get_wishlist(self, user_id: int) -> list[WishlistRecord]:
        pass

    @abstractmethod
    async def remove_wish(self, user_id: int, wish_id: int) -> bool:
        pass

    @abstractmethod
    async def create_wish(self, wish: WishlistRecord) -> bool:
        pass
