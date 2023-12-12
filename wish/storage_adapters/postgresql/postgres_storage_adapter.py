from logging import Logger
from typing import Any

from psycopg.errors import UniqueViolation, ProgrammingError
from psycopg.rows import class_row
from psycopg_pool import AsyncConnectionPool
from pydantic import ValidationError

from wish.storage_adapters.base_storage_adapter import WishStorageBaseAdapter
from wish.storage_adapters.postgresql.models.friend_model import FriendModel
from wish.storage_adapters.postgresql.models.user_model import UserModel
from wish.storage_adapters.postgresql.models.wish_model import WishModel
from wish.storage_adapters.postgresql.query_registry import QueryRegistry, SqlQuery
from wish.types.friend_record import FriendRecord
from wish.types.user import User
from wish.types.wish_record import WishRecord


class PostgresStorageAdapter(WishStorageBaseAdapter):
    def __init__(self, connection_name: str, db_connection: str, queries_registry_directory: str, logger: Logger):
        connections_count = 2
        self._pool = AsyncConnectionPool(db_connection,
                                         min_size=connections_count, max_size=connections_count,
                                         name=connection_name)
        self._query_registry = QueryRegistry(queries_registry_directory)
        self._logger = logger.getChild("postgresql-storage")

    @staticmethod
    def _convert_to_user_record(user_item: UserModel) -> User:
        return User(
            user_item.user_version,
            user_item.user_id,
            user_item.user_name,
            user_item.first_name,
            user_item.last_name,
            user_item.chat_id,
            user_item.wishlist_update_time
        )

    @staticmethod
    def _convert_to_wish_record(wish_item: WishModel) -> WishRecord:
        return WishRecord(
            wish_item.wish_id,
            wish_item.owner_id,
            wish_item.title,
            wish_item.hint,
            wish_item.cost,
            wish_item.reserved_by_user_id,
            performed=False
        )

    @staticmethod
    def _convert_to_friend_record(friend_item: FriendModel, user: User) -> FriendRecord:
        return FriendRecord(
            user,
            friend_item.request_counter,
            friend_item.access_time,
            friend_item.wishlist_seen_time
        )

    async def _process_query(self, query_id: SqlQuery, query_args: dict, cls=None, is_array: bool = False) -> (
            bool, Any | None):
        try:
            async with self._pool.connection() as con:
                row_factory = class_row(cls) if cls else None
                async with con.cursor(row_factory=row_factory) as cur:
                    query = self._query_registry.get_query(query_id)
                    await cur.execute(query, query_args)
                    if not row_factory:
                        return True, None

                    if not is_array:
                        return True, await cur.fetchone()

                    obj_list = []
                    async for obj in cur:
                        obj_list.append(obj)
                    return True, obj_list
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
            return self._convert_to_user_record(user_model)
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
        deleted, _ = await self._process_query(SqlQuery.DELETE_USER, {
            "user_id": user_id,
        })
        return deleted

    async def get_wishlist(self, user_id: int) -> list[WishRecord]:
        found, wish_items_list = await self._process_query(SqlQuery.GET_WISHLIST, {
            "owner_id": user_id
        }, WishModel, is_array=True)
        if not found:
            return []

        wishes: list[WishRecord] = []
        for wish_item in wish_items_list:
            wish = self._convert_to_wish_record(wish_item)
            wishes.append(wish)
        return wishes

    async def create_wish(self, wish: WishRecord) -> bool:
        created, _ = await self._process_query(SqlQuery.CREATE_WISH, {
            "owner_id": wish.owner_id,
            "title": wish.title,
            "hint": wish.hint,
            "cost": wish.cost,
            "reserved_by_user_id": wish.reserved_by_user_id,
        })
        return created

    async def get_wish(self, wish_id: int) -> WishRecord | None:
        found, wish_item = await self._process_query(SqlQuery.FIND_WISH_BY_ID, {
            "wish_id": wish_id,
        }, WishModel)
        wish_item: WishModel = wish_item
        if found and wish_item:
            return self._convert_to_wish_record(wish_item)
        return None

    async def update_wish(self, wish: WishRecord) -> bool:
        updated, _ = await self._process_query(SqlQuery.UPDATE_WISH, {
            "wish_id": wish.wish_id,
            "owner_id": wish.owner_id,
            "title": wish.title,
            "hint": wish.hint,
            "cost": wish.cost,
            "reserved_by_user_id": wish.reserved_by_user_id,
        })
        return updated

    async def remove_wish(self, user_id: int, wish_id: int) -> bool:
        removed, _ = await self._process_query(SqlQuery.DELETE_WISH, {
            "wish_id": wish_id,
        })
        return removed

    async def get_friend_list(self, user_id: int) -> list[FriendRecord]:
        found, friend_items_list = await self._process_query(SqlQuery.GET_FRIENDS_LIST, {
            "user_id": user_id
        }, FriendModel, is_array=True)

        if not found:
            return []

        friend_items_list: list[FriendModel] = friend_items_list
        friends: list[FriendRecord] = []
        for friend_item in friend_items_list:
            # todo: gather all async queries? or join its all in sql request?
            friend_user = await self.find_user_by_id(friend_item.friend_id)
            friend = self._convert_to_friend_record(friend_item, friend_user)
            friends.append(friend)
        return friends

    async def remove_friend(self, user_id: int, friend_id: int) -> bool:
        removed, _ = await self._process_query(SqlQuery.DELETE_FRIEND, {
            "user_id": user_id,
            "friend_id": friend_id,
        })
        return removed

    async def update_friend(self, user_id: int, friend_record: FriendRecord) -> bool:
        updated, _ = await self._process_query(SqlQuery.UPDATE_FRIEND, {
            "user_id": user_id,
            "friend_id": friend_record.user.id,
            "request_counter": friend_record.request_counter,
            "wishlist_seen_time": friend_record.last_wishlist_edit_time,
            "access_time": friend_record.last_access_time,
        })
        return updated

    async def create_friend(self, user_id: int, friend_record: FriendRecord) -> bool:
        created, _ = await self._process_query(SqlQuery.CREATE_FRIEND, {
            "user_id": user_id,
            "friend_id": friend_record.user.id,
            "request_counter": friend_record.request_counter,
            "access_time": friend_record.last_access_time,
            "wishlist_seen_time": friend_record.last_wishlist_edit_time,
        })
        return created

    async def find_user_friend_by_id(self, user_id: int, friend_id: int) -> FriendRecord | None:
        found, friend_item = await self._process_query(SqlQuery.FIND_FRIEND_BY_ID, {
            "user_id": user_id,
            "friend_id": friend_id,
        }, FriendModel)

        if found and friend_item:
            friend_item: FriendModel = friend_item
            friend_user = await self.find_user_by_id(friend_item.friend_id)
            return self._convert_to_friend_record(friend_item, friend_user)
        return None
