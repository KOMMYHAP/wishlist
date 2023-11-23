import json
import logging

from wish.storage_adapters.base_storage_adapter import WishStorageBaseAdapter
from wish.types.user import User
from wish.types.wishlist_record import WishlistRecord


class WishStorageMemoryAdapter(WishStorageBaseAdapter):
    users: dict[int, dict]
    wishes: dict[int, dict]

    def __init__(self):
        self.users = {}
        self.wishes = {}
        self._log = logging.getLogger('in-memory storage_adapters')

    async def get_user_by_name(self, username: str) -> User | None:
        for id, user_data in self.users.items():
            if user_data.get('user_name') != username:
                continue
            try:
                return User(user_data['user_id'], username)
            except KeyError as e:
                self._log.exception('username %s', username, exc_info=e)
                return None
        return None

    async def get_user_by_id(self, user_id: int) -> User | None:
        user = self.users.get(user_id)
        if user is None:
            return None
        try:
            return User(user['user_id'], user['user_name'])
        except KeyError as e:
            self._log.exception('user id %d, user data %s', user_id, json.dumps(user, indent='  '), exc_info=e)
            return None

    async def create_user(self, user: User) -> bool:
        old_user = self.users.get(user.id)
        if old_user is not None:
            return False
        user_data = {
            'user_id': user.id,
            'user_name': user.name
        }
        self.users[user.id] = user_data
        return True

    async def update_user(self, user: User) -> bool:
        user_data = self.users.get(user.id)
        if user_data is None:
            return False
        user_data['user_id'] = user.id
        user_data['user_name'] = user.name
        return True

    async def delete_user(self, user_id: int) -> bool:
        user_data = self.users.get(user_id)
        if user_data is None:
            return False
        self.users.pop(user_id)
        return True

    async def get_wishlist(self, user_id: int) -> list[WishlistRecord]:
        wishlist: list[WishlistRecord] = []
        for wish_id, wish_data in self.wishes.items():
            if wish_data['owner_id'] != user_id:
                continue
            wish = self._get_wish_record(wish_data)
            if wish is not None:
                wishlist.append(wish)
        return wishlist

    async def create_wish(self, wish: WishlistRecord) -> bool:
        wish.wish_id = len(self.wishes) + 1
        wish_data = self.wishes.get(wish.wish_id)
        if wish_data is not None:
            return False

        self.wishes[wish.wish_id] = {}
        await self.update_wish(wish)
        return True

    def _get_wish_record(self, wish_data: dict) -> WishlistRecord | None:
        try:
            return WishlistRecord(
                wish_data['wish_id'],
                wish_data['owner_id'],
                str(wish_data['title']),
                str(wish_data['hint']),
                wish_data['cost'],
                list(wish_data['references']),
                wish_data['reserved_by_user_id'],
                wish_data['performed']
            )
        except KeyError as e:
            self._log.exception('wish data %s', json.dumps(wish_data, indent='  '), exc_info=e)
            return None

    async def get_wish(self, wish_id: int) -> WishlistRecord | None:
        wish_data = self.wishes.get(wish_id)
        if wish_data is None:
            return None
        return self._get_wish_record(wish_data)

    async def update_wish(self, wish: WishlistRecord) -> bool:
        wish_data = self.wishes.get(wish.wish_id)
        if wish_data is None:
            return False

        wish_data['wish_id'] = wish.wish_id
        wish_data['owner_id'] = wish.owner_id
        wish_data['title'] = str(wish.title)
        wish_data['hint'] = str(wish.hint)
        wish_data['hint'] = wish.cost
        wish_data['references'] = list(wish.references)
        wish_data['reserved_by_user_id'] = wish.reserved_by_user_id
        wish_data['performed'] = wish.performed
        return True

    async def remove_wish(self, user_id: int, wish_id: int) -> bool:
        wish_data = self.wishes.get(wish_id)
        if wish_data is None:
            return False
        self.wishes.pop(wish_id)
        return True
