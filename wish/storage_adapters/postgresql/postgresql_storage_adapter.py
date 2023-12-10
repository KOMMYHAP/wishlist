from wish.storage_adapters.base_storage_adapter import WishStorageBaseAdapter
from wish.types.friend_record import FriendRecord
from wish.types.user import User
from wish.types.wish_record import WishRecord


class PostgresqlStorageAdapter(WishStorageBaseAdapter):
    async def find_user_by_name(self, username: str) -> User | None:
        pass

    async def find_user_by_id(self, user_id: int) -> User | None:
        pass

    async def create_user(self, user: User) -> bool:
        pass

    async def update_user(self, user: User) -> bool:
        pass

    async def delete_user(self, user_id: int) -> bool:
        pass

    async def get_wishlist(self, user_id: int) -> list[WishRecord]:
        pass

    async def create_wish(self, wish: WishRecord) -> bool:
        pass

    async def get_wish(self, wish_id: int) -> WishRecord | None:
        pass

    async def update_wish(self, wish: WishRecord) -> bool:
        pass

    async def remove_wish(self, user_id: int, wish_id: int) -> bool:
        pass

    async def get_friend_list(self, user_id: int) -> list[FriendRecord]:
        pass

    async def update_friend_list(self, user_id: int, friends: list[FriendRecord]) -> bool:
        pass

