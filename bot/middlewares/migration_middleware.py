import datetime
from logging import Logger

from telebot import SkipHandler
from telebot.asyncio_handler_backends import BaseMiddleware
from telebot.types import Message, User, CallbackQuery

from wish.wish_manager import WishManager


class MigrationMiddleware(BaseMiddleware):
    def __init__(self, wish_manager: WishManager, logger: Logger):
        super().__init__()
        self._wish_manager = wish_manager
        self._logger = logger.getChild('migration')
        self.update_types = ['message', 'callback_query']

    async def pre_process(self, message, data):
        user: User
        chat_id: int
        if isinstance(message, Message):
            user = message.from_user
            chat_id = message.chat.id
        elif isinstance(message, CallbackQuery):
            user = message.from_user
            chat_id = message.message.chat.id
        else:
            self._logger.error('Unknown message "%s"!', message)
            return SkipHandler()

        migrated = await self._migrate_user_data(user, chat_id)
        if not migrated:
            self._logger.error('Failed to migrate user %s (id %d)!', user.username, user.id)
            return SkipHandler()

    async def post_process(self, message, data, exception):
        pass

    async def _migrate_user_data(self, user: User, chat_id: int) -> bool:
        wishlist_user = await self._wish_manager.find_user_by_id(user.id)
        if wishlist_user is None:
            # nothing to migrate
            return True

        need_update = False
        initial_version = wishlist_user.version

        if wishlist_user.version == 0:
            wishlist_user.version = 1
            wishlist_user.first_name = user.first_name
            wishlist_user.last_name = user.last_name
            wishlist_user.chat_id = chat_id
            need_update = True
        if wishlist_user.version == 1:
            wishlist_user.version = 2
            wishlist_user.wishlist_update_time = datetime.datetime.now(datetime.UTC)
            need_update = True

        if not need_update:
            return True

        updated = await self._wish_manager.update_user(wishlist_user)
        if not updated:
            self._logger.error('Failed to migrate user %s (id %d) from version %s!',
                               user.username, user.id, initial_version)
            return False
        return True
