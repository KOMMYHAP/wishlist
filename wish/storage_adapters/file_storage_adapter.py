import json
import logging

from wish.storage_adapters.base_storage_adapter import WishStorageBaseAdapter
from wish.storage_adapters.memory_storage_adapter import WishStorageMemoryAdapter
from wish.types.friend_record import FriendRecord
from wish.types.user import User
from wish.types.wish_record import WishRecord


class WishStorageFileAdapter(WishStorageBaseAdapter):
    def __init__(self, filename: str, initial_wish_id: int):
        self._logger = logging.getLogger('file storage_adapters')
        self._memory_storage = WishStorageMemoryAdapter()
        self._filename = filename
        self._initial_wish_id = initial_wish_id

        self._load_from_file()

    async def find_user_by_name(self, username: str) -> User | None:
        return await self._memory_storage.find_user_by_name(username)

    async def find_user_by_id(self, user_id: int) -> User | None:
        return await self._memory_storage.find_user_by_id(user_id)

    async def create_user(self, user: User) -> bool:
        result = await self._memory_storage.create_user(user)
        if result:
            self._store_to_file()
        return result

    async def update_user(self, user: User) -> bool:
        result = await self._memory_storage.update_user(user)
        if result:
            self._store_to_file()
        return result

    async def delete_user(self, user_id: int) -> bool:
        result = await self._memory_storage.delete_user(user_id)
        if result:
            self._store_to_file()
        return result

    async def get_wishlist(self, user_id: int) -> list[WishRecord]:
        result = await self._memory_storage.get_wishlist(user_id)
        return result

    async def create_wish(self, wish: WishRecord) -> bool:
        result = await self._memory_storage.create_wish(wish)
        if result:
            self._store_to_file()
        return result

    async def get_wish(self, wish_id: int) -> WishRecord | None:
        result = await self._memory_storage.get_wish(wish_id)
        return result

    async def update_wish(self, wish: WishRecord) -> bool:
        result = await self._memory_storage.update_wish(wish)
        if result:
            self._store_to_file()
        return result

    async def remove_wish(self, user_id: int, wish_id: int) -> bool:
        result = await self._memory_storage.remove_wish(user_id, wish_id)
        if result:
            self._store_to_file()
        return result

    async def get_friend_list(self, user_id: int) -> list[FriendRecord]:
        return await self._memory_storage.get_friend_list(user_id)

    async def update_friend_list(self, user_id: int, friends: list[FriendRecord]) -> bool:
        result = await self._memory_storage.update_friend_list(user_id, friends)
        if result:
            self._store_to_file()
        return result

    def _load_from_file(self):
        try:
            with open(self._filename, 'r', encoding='utf-8') as f:
                root_data = json.load(f)
                self._memory_storage.wishes = {}
                for key, value in root_data['wishes'].items():
                    if 'cost' in value and isinstance(value['cost'], float):
                        value['cost'] = str(value['cost']) if value['cost'] > 0.0 else ''
                    self._memory_storage.wishes[int(key)] = value
                for key, value in root_data['users'].items():
                    self._memory_storage.users[int(key)] = value
                if root_data.get('friends') is not None:
                    for key, value in root_data['friends'].items():
                        self._memory_storage.users[int(key)] = value
                self._memory_storage.next_wish_id = root_data.get('next_wish_id', self._initial_wish_id)
        except FileNotFoundError:
            self._logger.debug('File %s was not found', self._filename)
        except OSError as io_error:
            self._logger.exception('Failed to store data to file %s', self._filename, exc_info=io_error)

    def _store_to_file(self):
        try:
            with open(self._filename, 'w', encoding='utf-8') as f:
                root_data = {
                    'users': self._memory_storage.users,
                    'wishes': self._memory_storage.wishes,
                    'friends': self._memory_storage.friends,
                    'next_wish_id': self._memory_storage.next_wish_id
                }
                json.dump(root_data, f, indent='   ')
        except OSError as io_error:
            self._logger.exception('Failed to store data to file %s', self._filename, exc_info=io_error)
