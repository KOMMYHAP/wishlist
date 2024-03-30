import argparse
import asyncio
import logging
from asyncio import WindowsSelectorEventLoopPolicy

from wish.migration.migration_to_postgresql import perform_migration
from wish.storage_adapters.file_storage_adapter import WishStorageFileAdapter
from wish.storage_adapters.postgresql.postgres_storage_adapter import PostgresStorageAdapter


async def entry_point() -> None:
    parser = argparse.ArgumentParser("Migration Tool")
    parser.add_argument('--storage-file')

    parser.add_argument('--database-name')
    parser.add_argument('--database-username')
    parser.add_argument('--database-password')
    parser.add_argument('--database-queries-directory')
    args = parser.parse_args()

    root_logger = logging.getLogger()

    fake_initial_wish_id = 0
    file_storage = WishStorageFileAdapter(args.storage_file, fake_initial_wish_id)

    dbname = args.database_name
    user = args.database_username
    password = args.database_password
    queries_directory = args.database_queries_directory
    con = f"dbname={dbname} user={user} password={password}"
    database_storage = PostgresStorageAdapter("wishlist-bot", con, queries_directory, root_logger)

    await perform_migration(root_logger, file_storage.memory_storage, database_storage)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    asyncio.run(entry_point())
