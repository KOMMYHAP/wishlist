import json
import logging

from wish.storage_adapters.base_storage_adapter import WishStorageBaseAdapter
from wish.storage_adapters.memory_storage_adapter import WishStorageMemoryAdapter
from wish.types.user import User
from wish.types.wishlist_record import WishlistRecord


class WishStorageFileAdapter(WishStorageBaseAdapter):
    def __init__(self, filename: str):
        self._logger = logging.getLogger('file storage_adapters')
        self._memory_storage = WishStorageMemoryAdapter()
        self._filename = filename

        self._load_from_file()

    async def get_user_by_name(self, username: str) -> User | None:
        return await self._memory_storage.get_user_by_name(username)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self._memory_storage.get_user_by_id(user_id)

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

    async def get_wishlist(self, user_id: int) -> list[WishlistRecord]:
        result = await self._memory_storage.get_wishlist(user_id)
        return result

    async def create_wish(self, wish: WishlistRecord) -> bool:
        result = await self._memory_storage.create_wish(wish)
        if result:
            self._store_to_file()
        return result

    async def get_wish(self, wish_id: int) -> WishlistRecord | None:
        result = await self._memory_storage.get_wish(wish_id)
        return result

    async def update_wish(self, wish: WishlistRecord) -> bool:
        result = await self.update_wish(wish)
        if result:
            self._store_to_file()
        return result

    async def remove_wish(self, user_id: int, wish_id: int) -> bool:
        result = await self._memory_storage.remove_wish(user_id, wish_id)
        if result:
            self._store_to_file()
        return result

    def _load_from_file(self):
        try:
            with open(self._filename, 'r', encoding='utf-8') as f:
                # root_data = _byteify(json.load(f, object_hook=_byteify), ignore_dicts=True)
                root_data = json.load(f)
                self._memory_storage.wishes = {}
                for key, value in root_data['wishes'].items():
                    self._memory_storage.wishes[int(key)] = value
                for key, value in root_data['users'].items():
                    self._memory_storage.users[int(key)] = value
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
                }
                json.dump(root_data, f, indent='   ')
        except OSError as io_error:
            self._logger.exception('Failed to store data to file %s', self._filename, exc_info=io_error)
