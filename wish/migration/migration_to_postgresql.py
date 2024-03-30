from logging import Logger

from wish.storage_adapters.memory_storage_adapter import WishStorageMemoryAdapter
from wish.storage_adapters.postgresql.postgres_storage_adapter import PostgresStorageAdapter


async def perform_migration(logger: Logger, memory_storage: WishStorageMemoryAdapter,
                            database_storage: PostgresStorageAdapter) -> bool:
    for user_id in memory_storage.users.keys():
        user_data = await memory_storage.find_user_by_id(user_id)
        if not user_data:
            logger.error('Invalid user stored by id %d!', user_id)
            return False
        if not await database_storage.create_user(user_data):
            logger.error('Failed to create user %d!', user_id)
            return False

    for user_id in memory_storage.users.keys():
        friend_list = await memory_storage.get_friend_list(user_id)
        for friend_record in friend_list:
            if not await database_storage.create_friend(user_id, friend_record):
                logger.error('Failed to create friend %d for user %d!', friend_record.user.id, user_id)
                return False

    for wish_id in memory_storage.wishes.keys():
        wish_data = await memory_storage.get_wish(wish_id)
        if not wish_data:
            logger.error('Invalid wish stored by id %d!', wish_id)
            return False
        if not await database_storage.create_wish(wish_data):
            logger.error('Failed to create wish %d!', wish_id)
            return False

    return True
