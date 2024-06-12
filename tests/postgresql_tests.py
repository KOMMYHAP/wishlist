import argparse
import asyncio
import datetime
import logging
from asyncio import WindowsSelectorEventLoopPolicy
from logging import Logger

from wish.storage_adapters.postgresql.postgres_storage_adapter import PostgresStorageAdapter
from wish.types.user import User


async def postgresql_tests_entry_point() -> None:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    parser = argparse.ArgumentParser("PostgresSQL Tests")
    parser.add_argument('--database-name', required=True)
    parser.add_argument('--database-username', required=True)
    parser.add_argument('--database-password', required=True)
    parser.add_argument('--database-queries-directory', required=True)
    args = parser.parse_args()

    dbname = args.database_name
    user = args.database_username
    password = args.database_password
    queries_directory = args.database_queries_directory
    con = f"dbname={dbname} user={user} password={password}"
    logger = Logger.root

    adapter = PostgresStorageAdapter("wishlist-tests", con, logger)

    now = datetime.datetime.now(datetime.UTC)
    user = User(1, 42, 'username', 'first_name', 'last_name', 10, now)
    created = await adapter.create_user(user)
    logger.info('user %s', "created" if created else "not created")
    user.username = 'White'
    user.version = 2
    updated = await adapter.update_user(user)
    logger.info('user %s', "updated" if updated else "not updated")

    found_user = await adapter.find_user_by_id(42)
    if found_user:
        logger.info('user %d found!', found_user.id)

    found_user = await adapter.find_user_by_name('username')
    if not found_user:
        logger.info('another user by name %s was not found!', 'username')

    found_user = await adapter.find_user_by_name('White')
    if found_user:
        logger.info('another user by name %s (id: %d) was found!', 'White', found_user.id)

    user_2 = User(1, 43, 'White', 'first_name_2', 'last_name_2', 10, now)
    await adapter.create_user(user_2)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    asyncio.run(postgresql_tests_entry_point())
