import json
import logging
from logging import Logger

from telegram.ext import BasePersistence

from data_types import User, WishlistRecord
from storage_interface import BaseStorage


class LocalStorage(BaseStorage):
    _persistence: BasePersistence
    _log: Logger

    def __init__(self, persistence: BasePersistence):
        self._persistence = persistence
        self._log = logging.getLogger("LocalStorage")

    async def get_user_by_name(self, username: str) -> User | None:
        user_data = await self._persistence.get_user_data()
        try:
            for id, data in user_data.items():
                if data['user_name'] == username:
                    return User(data['user_id'], data['user_name'])
        except KeyError as e:
            self._log.exception('username %s', username, exc_info=e)
            return None
        return None

    async def get_user_by_id(self, user_id: int) -> User | None:
        user_data = await self._persistence.get_user_data()
        user = user_data.get(user_id)
        if user is None:
            return None

        try:
            return User(user['user_id'], user['user_name'])
        except KeyError as e:
            self._log.exception('user id %d', user_id, exc_info=e)
            return None

    async def create_user(self, user: User) -> bool:
        old_user = self.get_user_by_id(user.id)
        if old_user:
            return False
        await self._update_user_data(user.id, {
            'user_id': user.id,
            'user_name': user.name,
            'wishlist': []
        })
        return True

    async def get_wishlist(self, user_id: int) -> list[WishlistRecord]:
        wishlist_records = []
        user_data = await self._persistence.get_user_data()
        user = user_data.get(user_id)
        if user is None:
            return []
        try:
            for wish in user['wishlist']:
                record = WishlistRecord(
                    wish['id'],
                    wish['user_id'],
                    wish['title'],
                    wish['references'],
                    wish['reserved_by_user'],
                    wish['performed']
                )
                wishlist_records.append(record)
        except KeyError as e:
            self._log.exception('user id %d', user_id, exc_info=e)
            return []
        return wishlist_records

    async def remove_wish(self, user_id: int, wish_idx: int) -> bool:
        user_data = await self._persistence.get_user_data()
        user = user_data.get(user_id)
        if user is None:
            return False

        try:
            wish = user['wishlist'][wish_idx]
            wish.performed = True
            await self._update_user_data(user_id, user)
        except KeyError as e:
            self._log.exception('user id %d, wish_idx %d', user_id, wish_idx, exc_info=e)
            return False
        return True

    async def create_wish(self, wish: WishlistRecord) -> bool:
        bot_data = await self._persistence.get_bot_data()

        if bot_data.get('wish_id') is None:
            bot_data['wish_id'] = 0
        wish_id = bot_data['wish_id']
        bot_data['wish_id'] = wish_id + 1
        await self._update_bot_data(bot_data)

        user_data = await self._persistence.get_user_data()
        user = user_data.get(wish.user_id)
        if user is None:
            return False

        try:
            wish_entry = {
                'id': wish_id,
                'user_id': wish.user_id,
                'title': wish.title,
                'references': wish.references,
                'reserved_by_user': wish.reserved_by_user,
                'performed': wish.performed
            }
            user['whishlist'].append(wish_entry)
            await self._update_user_data(wish.user_id, wish_entry)
        except KeyError as e:
            self._log.exception('user id %d, wish %s', wish.user_id, str(wish), exc_info=e)
            return False
        return True

    async def _update_user_data(self, user_id: int, user_data: dict) -> None:
        old_user_data = await self._persistence.get_user_data()
        await self._persistence.update_user_data(user_id, user_data)
        dump_1 = json.dumps(old_user_data, indent='  ')
        dump_2 = json.dumps(user_data, indent='  ')
        self._log.debug('update user data of user %d from: \n%s, to: \n%s', user_id, dump_1, dump_2)

    async def _update_bot_data(self, bot_data: dict) -> None:
        old_bot_data = None
        if self._log.isEnabledFor(logging.DEBUG):
            old_bot_data = await self._persistence.get_bot_data()

        await self._persistence.update_bot_data(bot_data)

        if self._log.isEnabledFor(logging.DEBUG):
            dump_1 = json.dumps(old_bot_data, indent='  ')
            dump_2 = json.dumps(bot_data, indent='  ')
            self._log.debug('update bot data from: \n%s, to: \n%s', dump_1, dump_2)
