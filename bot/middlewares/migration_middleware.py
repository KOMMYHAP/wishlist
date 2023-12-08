import datetime
from logging import Logger

from telebot import SkipHandler
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_handler_backends import BaseMiddleware
from telebot.types import Message, CallbackQuery, BotCommand
from telebot.types import User as TelegramUser

from bot.handlers.command_registry import WishlistCommands, get_command_description
from bot.version import get_update_message, current_bot_version
from wish.types.user import User as WishUser
from wish.wish_manager import WishManager


class MigrationMiddleware(BaseMiddleware):
    def __init__(self, wish_manager: WishManager, logger: Logger, bot: AsyncTeleBot):
        super().__init__()
        self._wish_manager = wish_manager
        self._logger = logger.getChild('migration')
        self._bot = bot
        self.update_types = ['message', 'callback_query']

    async def pre_process(self, message, data):
        user: TelegramUser
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

    async def _migrate_user_data(self, user: TelegramUser, chat_id: int) -> bool:
        wishlist_user = await self._wish_manager.find_user_by_id(user.id)
        if wishlist_user is None:
            # nothing to migrate
            return True

        need_update = False
        initial_version = wishlist_user.version

        need_update |= initial_version < current_bot_version
        need_update |= self._migrate_to_v1(chat_id, user, wishlist_user)
        need_update |= self._migrate_to_v2(wishlist_user)

        if not need_update:
            return True

        wishlist_user.version = current_bot_version
        updated = await self._wish_manager.update_user(wishlist_user)
        if not updated:
            self._logger.error('Failed to migrate user %s (id %d) from version %s!',
                               user.username, user.id, initial_version)
            return False

        await self._print_update_messages(chat_id, initial_version)
        await self._update_commands_list()
        return True

    async def _print_update_messages(self, chat_id, initial_version):
        update_message = get_update_message(initial_version)
        if update_message:
            await self._bot.send_message(chat_id, update_message)

    async def _update_commands_list(self):
        bot_commands: list[BotCommand] = []
        for wishlist_command in WishlistCommands:
            bot_commands.append(
                BotCommand(command=wishlist_command.value, description=get_command_description(wishlist_command)))
        await self._bot.set_my_commands(bot_commands)

    @staticmethod
    def _migrate_to_v1(chat_id: int, user: TelegramUser, wishlist_user: WishUser):
        if wishlist_user.version != 0:
            return False
        wishlist_user.version = 1
        wishlist_user.first_name = user.first_name
        wishlist_user.last_name = user.last_name
        wishlist_user.chat_id = chat_id
        return True

    @staticmethod
    def _migrate_to_v2(wishlist_user: WishUser):
        if wishlist_user.version != 1:
            return False
        wishlist_user.version = 2
        wishlist_user.wishlist_update_time = datetime.datetime.now(datetime.UTC)
        return True
