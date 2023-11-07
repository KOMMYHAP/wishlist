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


class WishBuilder:
    title: str
    references: list[str]


class WishManager:
    _storage: BaseStorage
    _backtrace: Logger
    _incomplete_wish_by_user: dict[int, WishBuilder]

    def __init__(self, storage: BaseStorage):
        self._storage = storage
        self._backtrace = logging.getLogger('WishManager::Backtrace')
        self._backtrace.disabled = False
        self._incomplete_wish_by_user = {}
        pass

    async def get_wishlist(self, user_id: int, target_username: str) -> WishlistResponse:
        self._backtrace.info('get_wishlist(%d, %s)', user_id, target_username)

        target_user = await self._storage.get_user_by_name(target_username)
        if target_user is None:
            self._backtrace.info('get_wishlist(%d, %s) -> unknown target user', user_id, target_username)
            return WishlistResponse([], None)

        wishlist = await self._storage.get_wishlist(target_user.id)
        response = WishlistResponse(wishlist, target_user, {})
        for wish in wishlist:
            if wish.reserved_by_user is None:
                continue
            reserved_by_user = await self._storage.get_user_by_id(wish.user_id)
            response.reservation_map[wish.wish_id] = reserved_by_user
        return response

    async def add_wish_title(self, user_id: int, title: str) -> None:
        self._backtrace.info('add_wish_title(%d, %s)', user_id, title)
        await self._try_complete_wish(user_id)
        self._require_wish_builder(user_id).title = title

    async def add_wish_reference(self, user_id: int, reference: str) -> None:
        self._backtrace.info('add_wish_reference(%d, %s)', user_id, reference)
        builder = self._require_wish_builder(user_id)
        if builder.references is None:
            builder.references = []
        builder.references.append(reference)

    async def remove_incomplete_wish(self, user_id: int) -> None:
        self._backtrace.info('remove_incomplete_wish(%d)', user_id)
        self._discard_wish_builder(user_id)

    async def remove_wish(self, user_id: int, wish_idx: int) -> bool:
        wishlist = await self._storage.get_wishlist(user_id)
        if not (0 <= wish_idx < len(wishlist)):
            self._backtrace.info(f'remove_wish(%d, %d) -> wish idx must be in range [%d; %d)', user_id, wish_idx, 0,
                                 len(wishlist))
            return False

        wish = wishlist[wish_idx]
        removed = await self._storage.remove_wish(user_id, wish_idx)
        if removed:
            self._backtrace.info(f'remove_wish(%d, %d) -> wish %d removed', user_id, wish_idx, wish.wish_id)
        else:
            self._backtrace.info(f'remove_wish(%d, %d) -> failed to remove wish %d', user_id, wish_idx, wish.wish_id)
        return removed

    async def register_user(self, user: User) -> bool:
        old_user = await self._storage.get_user_by_id(user.id)
        if old_user is None:
            await self._storage.create_user(user)
            self._backtrace.info('register_user(%d) -> new user created', user.id)
            return True
        self._backtrace.info('register_user(%d) -> user found', user.id)
        return False

    async def _try_complete_wish(self, user_id: int) -> bool:
        wish_builder = self._incomplete_wish_by_user.get(user_id)
        if wish_builder is None:
            self._backtrace.info('_try_complete_wish(%d) -> no incomplete wish', user_id)
            return False

        if wish_builder.title is None:
            self._backtrace.info('_try_complete_wish(%d) -> invalid title', user_id)
            return False

        unknown_id = 0
        wish = WishlistRecord(unknown_id, user_id, wish_builder.title, wish_builder.references or [], None, False)
        await self._storage.create_wish(wish)
        self._backtrace.info("_try_complete_wish(%d) -> wish '%s' completed", user_id, wish_builder.title)
        return True

    def _require_wish_builder(self, user_id: int) -> WishBuilder:
        wish_builder = self._incomplete_wish_by_user.get(user_id)
        if wish_builder is None:
            builder = WishBuilder()
            self._incomplete_wish_by_user[user_id] = builder
            self._backtrace.info("_discard_wish_builder(%d) -> wish builder created", user_id)
        return wish_builder

    def _discard_wish_builder(self, user_id: int) -> None:
        if self._incomplete_wish_by_user.get(user_id):
            self._incomplete_wish_by_user.pop(user_id)
            self._backtrace.info("_discard_wish_builder(%d) -> incomplete wish discarded", user_id)
        else:
            self._backtrace.info("_discard_wish_builder(%d) -> incomplete wish not found", user_id)
