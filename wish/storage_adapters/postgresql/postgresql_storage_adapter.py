from datetime import datetime
from logging import Logger
from typing import Any

from psycopg.errors import UniqueViolation, ProgrammingError
from psycopg.rows import class_row
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, ValidationError

from wish.storage_adapters.base_storage_adapter import WishStorageBaseAdapter
from wish.storage_adapters.postgresql.query_registry import QueryRegistry, SqlQuery
from wish.types.friend_record import FriendRecord
from wish.types.user import User
from wish.types.wish_record import WishRecord


class UserModel(BaseModel):
    user_id: int
    user_name: str
    first_name: str
    last_name: str
    chat_id: int
    wishlist_update_time: datetime
    user_version: int


class PostgresqlStorageAdapter(WishStorageBaseAdapter):
    def __init__(self, connection_name: str, db_connection: str, queries_registry_directory: str, logger: Logger):
        connections_count = 2
        self._pool = AsyncConnectionPool(db_connection,
                                         min_size=connections_count, max_size=connections_count,
                                         name=connection_name)
        self._query_registry = QueryRegistry(queries_registry_directory)
        self._logger = logger.getChild("postgresql-storage")

    async def _process_query(self, query_id: SqlQuery, query_args: dict, cls=None) -> (bool, Any | None):
        try:
            async with self._pool.connection() as con:
                row_factory = class_row(cls) if cls else None
                async with con.cursor(row_factory=row_factory) as cur:
                    query = self._query_registry.get_query(query_id)
                    await cur.execute(query, query_args)
                    if row_factory:
                        obj = await cur.fetchone()
                        return True, obj
                    return True, None
        except UniqueViolation as e:
            self._logger.error("Unique violation! Details: %s", e.diag.message_detail or 'no details.')
        except ValidationError as e:
            self._logger.exception("Validation error!", exc_info=e)
        except ProgrammingError as e:
            self._logger.exception("Programming error!", exc_info=e)
        except BaseException as e:
            self._logger.exception("Unknown error occurred!", exc_info=e)
        return False, None

    async def find_user_by_name(self, username: str) -> User | None:
        found, user_model = await self._process_query(SqlQuery.FIND_USER_BY_NAME, {
            "user_name": username,
        }, UserModel)

        if found and user_model:
            return User(user_model.user_version, user_model.user_id,
                        user_model.user_name, user_model.first_name, user_model.last_name,
                        user_model.chat_id, user_model.wishlist_update_time)
        return None

    async def find_user_by_id(self, user_id: int) -> User | None:
        found, user_model = await self._process_query(SqlQuery.FIND_USER_BY_ID, {
            "user_id": user_id,
        }, UserModel)

        if found and user_model:
            return User(user_model.user_version, user_model.user_id,
                        user_model.user_name, user_model.first_name, user_model.last_name,
                        user_model.chat_id, user_model.wishlist_update_time)
        return None

    async def create_user(self, user: User) -> bool:
        created, _ = await self._process_query(SqlQuery.CREATE_USER, {
            "user_id": user.id,
            "user_name": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "chat_id": user.chat_id,
            "wishlist_update_time": user.wishlist_update_time,
            "user_version": user.version,
        })
        return created

    async def update_user(self, user: User) -> bool:
        updated, _ = await self._process_query(SqlQuery.UPDATE_USER, {
            "user_id": user.id,
            "user_name": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "chat_id": user.chat_id,
            "wishlist_update_time": user.wishlist_update_time,
            "user_version": user.version,
        })
        return updated

    async def delete_user(self, user_id: int) -> bool:
        pass

    async def get_wishlist(self, user_id: int) -> list[WishRecord]:
        pass

    async def create_wish(self, wish: WishRecord) -> bool:
        pass

    async def get_wish(self, wish_id: int) -> WishRecord | None:
        pass

    async def update_wish(self, wish: WishRecord) -> bool:
        pass

    async def remove_wish(self, user_id: int, wish_id: int) -> bool:
        pass

    async def get_friend_list(self, user_id: int) -> list[FriendRecord]:
        pass

    async def update_friend_list(self, user_id: int, friends: list[FriendRecord]) -> bool:
        pass
