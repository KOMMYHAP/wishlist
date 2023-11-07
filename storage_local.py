from telegram.ext import PicklePersistence

from data_types import User, WishlistRecord
from storage_interface import BaseStorage


class LocalStorage(BaseStorage):
    def __init__(self, persistence: PicklePersistence):
        self.persistence = persistence

    async def get_user_by_name(self, username: str) -> User | None:
        user_data = await self.persistence.get_user_data()
        for id, data in user_data.items():
            if data['user_name'] == username:
                return User(data['user_id'], data['user_name'])
        return None

    async def get_user_by_id(self, user_id: int) -> User | None:
        user_data = await self.persistence.get_user_data()
        user = user_data.get(user_id)
        if user is None:
            return None

        return User(user['user_id'], user['user_name'])

    async def create_user(self, user: User) -> bool:
        await self.persistence.update_user_data(user.id, {
            'user_id': user.id,
            'user_name': user.name
        })
        return True

    async def get_wishlist(self, user_id: int) -> list[WishlistRecord]:
        wishlist_records = []
        user_data = await self.persistence.get_user_data()
        for id, data in user_data.items():
            if id != user_id:
                continue
            for wish in data.get('wishlist', []):
                record = WishlistRecord(
                    wish['id'],
                    wish['user_id'],
                    wish['title'],
                    wish['references'],
                    wish['reserved_by_user'],
                    wish['performed']
                )
                wishlist_records.append(record)
            break
        return wishlist_records

    async def remove_wish(self, user_id: int, wish_id: int) -> bool:
        user_data = await self.persistence.get_user_data()
        for id, data in user_data.items():
            if id != user_id:
                continue
            for wish_idx in range(0, len(data['wishlist'])):
                wish = data['wishlist'][wish_idx]
                if wish['id'] != wish_id:
                    continue
                wish.performed = True
                await self.persistence.update_user_data(user_id, data)
                break
            break
        return True

    async def create_wish(self, wish: WishlistRecord) -> bool:
        bot_data = await self.persistence.get_bot_data()

        if bot_data.get('wish_id') is None:
            bot_data['wish_id'] = 0
        wish_id = bot_data['wish_id']
        bot_data['wish_id'] = wish_id + 1
        await self.persistence.update_bot_data(bot_data)

        user_data = await self.persistence.get_user_data()
        for id, data in user_data.items():
            if id != wish.user_id:
                continue

            wish_entry = {
                'id': wish_id,
                'user_id': wish.user_id,
                'title': wish.title,
                'references': wish.references,
                'reserved_by_user': wish.reserved_by_user,
                'performed': wish.performed
            }
            if data.get('wishlist') is None:
                data['whishlist'] = []
            data['whishlist'].append(wish_entry)
            await self.persistence.update_user_data(wish.user_id, data)
            break
        return True
