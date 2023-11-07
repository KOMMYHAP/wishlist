import logging
from dataclasses import dataclass
from logging import Logger

from data_types import WishlistRecord, User
from storage_interface import BaseStorage


@dataclass
class WishlistResponse:
    wishlist: list[WishlistRecord]
    owner: User | None
    reservation_map: dict[int, User]


@dataclass
class WishBuilder:
    title: str | None
    references: list[str] | None


class WishManager:
    _storage: BaseStorage
    _log: Logger
    _incomplete_wish_by_user: dict[int, WishBuilder]

    def __init__(self, storage: BaseStorage):
        self._storage = storage
        self._log = logging.getLogger('WishManager')
        self._log.setLevel(logging.DEBUG)
        self._incomplete_wish_by_user = {}
        pass

    async def get_wishlist(self, user_id: int, target_username: str) -> WishlistResponse:
        self._log.debug('get_wishlist(%d, %s)', user_id, target_username)

        await self._try_complete_wish(user_id)

        target_user = await self._storage.get_user_by_name(target_username)
        if target_user is None:
            self._log.debug('get_wishlist(%d, %s) -> unknown target user', user_id, target_username)
            return WishlistResponse([], None, {})

        wishlist = await self._storage.get_wishlist(target_user.id)
        response = WishlistResponse(wishlist, target_user, {})
        for wish in wishlist:
            if wish.reserved_by_user is None:
                continue
            reserved_by_user = await self._storage.get_user_by_id(wish.user_id)
            response.reservation_map[wish.wish_id] = reserved_by_user
        return response

    async def add_wish_title(self, user_id: int, title: str) -> None:
        self._log.debug('add_wish_title(%d, %s)', user_id, title)
        await self._try_complete_wish(user_id)
        self._require_wish_builder(user_id).title = title
        self._log.debug('add_wish_title(%d, %s) -> wish builder updated', user_id, title)

    async def add_wish_reference(self, user_id: int, reference: str) -> None:
        self._log.debug('add_wish_reference(%d, %s)', user_id, reference)
        builder = self._require_wish_builder(user_id)
        if builder.references is None:
            builder.references = []
        builder.references.append(reference)
        self._log.debug('add_wish_reference(%d, %s) -> wish builder updated', user_id, reference)

    async def remove_incomplete_wish(self, user_id: int) -> None:
        self._log.debug('remove_incomplete_wish(%d)', user_id)
        self._discard_wish_builder(user_id)

    async def remove_wish(self, user_id: int, wish_idx: int) -> bool:
        self._log.debug('remove_wish(%d, %d)', user_id, wish_idx)

        await self._try_complete_wish(user_id)

        wishlist = await self._storage.get_wishlist(user_id)
        if not (0 <= wish_idx < len(wishlist)):
            self._log.debug(f'remove_wish(%d, %d) -> wish idx must be in range [%d; %d)', user_id, wish_idx, 0,
                            len(wishlist))
            return False

        wish = wishlist[wish_idx]
        removed = await self._storage.remove_wish(user_id, wish_idx)
        if removed:
            self._log.debug(f'remove_wish(%d, %d) -> wish %d removed', user_id, wish_idx, wish.wish_id)
        else:
            self._log.error(f'remove_wish(%d, %d) -> failed to remove wish %d', user_id, wish_idx, wish.wish_id)
        return removed

    async def register_user(self, user: User) -> bool:
        old_user = await self._storage.get_user_by_id(user.id)
        if old_user is None:
            created = await self._storage.create_user(user)
            if not created:
                self._log.error('register_user(%s) -> failed to create new user', str(user))
                return False
            self._log.debug('register_user(%s) -> new user created', str(user))
            return True
        self._log.debug('register_user(%s) -> user found', str(user))
        return False

    async def _try_complete_wish(self, user_id: int) -> bool:
        self._log.debug('_try_complete_wish(%d)', user_id)
        wish_builder = self._incomplete_wish_by_user.get(user_id)
        if wish_builder is None:
            self._log.debug('_try_complete_wish(%d) -> no incomplete wish', user_id)
            return False

        if wish_builder.title is None:
            self._log.error('_try_complete_wish(%d) -> invalid title', user_id)
            return False

        unknown_id = 0
        wish = WishlistRecord(unknown_id, user_id, wish_builder.title, wish_builder.references or [], None, False)
        created = await self._storage.create_wish(wish)

        if created:
            self._incomplete_wish_by_user.pop(user_id)
            self._log.debug("_try_complete_wish(%d) -> wish '%s' completed", user_id, str(wish))
            return True
        else:
            self._log.error("_try_complete_wish(%d) -> failed to complete wish '%s'", user_id, str(wish))
            return False

    def _require_wish_builder(self, user_id: int) -> WishBuilder:
        wish_builder = self._incomplete_wish_by_user.get(user_id)
        if wish_builder is None:
            wish_builder = WishBuilder(None, None)
            self._incomplete_wish_by_user[user_id] = wish_builder
            self._log.debug("_require_wish_builder(%d) -> wish builder created", user_id)
        return wish_builder

    def _discard_wish_builder(self, user_id: int) -> None:
        if self._incomplete_wish_by_user.get(user_id):
            self._incomplete_wish_by_user.pop(user_id)
            self._log.debug("_discard_wish_builder(%d) -> incomplete wish discarded", user_id)
        else:
            self._log.debug("_discard_wish_builder(%d) -> incomplete wish not found", user_id)
