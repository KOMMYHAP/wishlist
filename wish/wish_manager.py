from dataclasses import dataclass
from logging import Logger

from bot.handlers.wish_editor.wish_editor_draft import WishEditorDraft
from bot.handlers.wish_viewer.wish_viewer_draft import WishViewerDraft
from wish.storage_adapters.base_storage_adapter import WishStorageBaseAdapter
from wish.types.user import User
from wish.types.wish_record import WishRecord
from wish.wishlist_config import WishlistConfig


@dataclass
class WishlistResponse:
    wishlist: list[WishRecord]
    owner: User | None
    reservation_map: dict[int, User]


class WishManager:
    _storage: WishStorageBaseAdapter
    _log: Logger
    config: WishlistConfig

    def __init__(self, storage: WishStorageBaseAdapter, logger: Logger, config: WishlistConfig):
        self._storage = storage
        self._log = logger.getChild('wish_manager')
        self._incomplete_wish_by_user = {}
        self.config = config

    async def find_user_by_id(self, user_id: int) -> User | None:
        self._log.debug('find_username(%d)', user_id)
        return await self._storage.find_user_by_id(user_id)

    async def find_user_by_name(self, user_name: str) -> User | None:
        self._log.debug('find_user_id(%s)', user_name)
        return await self._storage.find_user_by_name(user_name)

    async def get_wish(self, wish_id: int) -> WishRecord | None:
        self._log.debug('get_wish(%d)', wish_id)
        return await self._storage.get_wish(wish_id)

    async def update_wish_by_editor(self, editor_user_id: int, wish_draft: WishEditorDraft) -> bool:
        self._log.debug('update_wish(%d, %s)', editor_user_id, str(wish_draft))
        old_wish = await self.get_wish(wish_draft.wish_id)
        if old_wish is None:
            self._log.error('wish %d was not found to update!', wish_draft.wish_id)
            return False
        if old_wish.performed:
            self._log.warning('trying to update wish which is already performed')
            return False
        return await self._storage.update_wish(WishRecord(
            wish_draft.wish_id,
            editor_user_id,
            wish_draft.title,
            wish_draft.hint,
            wish_draft.cost,
            old_wish.reserved_by_user_id,
            old_wish.performed
        ))

    async def update_wish_by_viewer(self, viewer_user_id: int, wish_viewer_draft: WishViewerDraft) -> bool:
        self._log.debug('update_wish(%d, %s)', viewer_user_id, str(wish_viewer_draft))
        old_wish = await self.get_wish(wish_viewer_draft.wish_id)
        if old_wish is None:
            self._log.error('wish %d was not found to update!', wish_viewer_draft.wish_id)
            return False
        if old_wish.performed:
            self._log.warning('trying to update wish which is already performed')
            return False
        if wish_viewer_draft.reserved and old_wish.reserved_by_user_id is not None:
            self._log.warning('trying to reserve with which is already reserved!')
            return False

        reserved_by_user_id: int | None = old_wish.reserved_by_user_id
        if wish_viewer_draft.reserved:
            reserved_by_user_id = viewer_user_id

        return await self._storage.update_wish(WishRecord(
            wish_viewer_draft.wish_id,
            old_wish.owner_id,
            old_wish.title,
            old_wish.hint,
            old_wish.cost,
            reserved_by_user_id,
            old_wish.performed
        ))

    async def create_wish(self, user_id: int, wish_draft: WishEditorDraft) -> bool:
        self._log.debug('create_wish(%d, %s)', user_id, str(wish_draft))
        return await self._storage.create_wish(WishRecord(
            0,
            user_id,
            wish_draft.title,
            wish_draft.hint,
            wish_draft.cost,
            None,
            False
        ))

    async def get_wishlist(self, user_id: int, target_user_id: int) -> WishlistResponse:
        self._log.debug('get_wishlist(%d, %d)', user_id, target_user_id)

        target_user = await self._storage.find_user_by_id(target_user_id)
        if target_user is None:
            self._log.debug('get_wishlist(%d, %d) -> unknown target user', user_id, target_user_id)
            return WishlistResponse([], None, {})

        wishlist = await self._storage.get_wishlist(target_user.id)
        response = WishlistResponse(wishlist, target_user, {})
        for wish in wishlist:
            if wish.reserved_by_user_id is None:
                continue
            reserved_by_user = await self._storage.find_user_by_id(wish.owner_id)
            response.reservation_map[wish.wish_id] = reserved_by_user
        return response

    async def remove_wish(self, user_id: int, wish_idx: int) -> bool:
        self._log.debug('remove_wish(%d, %d)', user_id, wish_idx)

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
        old_user = await self._storage.find_user_by_id(user.id)
        if old_user is not None:
            self._log.debug('register_user(%s) -> user found', str(user))
            return False

        created = await self._storage.create_user(user)
        if not created:
            self._log.error('register_user(%s) -> failed to create new user', str(user))
            return False
        self._log.debug('register_user(%s) -> new user created', str(user))
        return True
