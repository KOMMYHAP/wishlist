import os.path
from enum import StrEnum


class SqlQuery(StrEnum):
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    FIND_USER_BY_ID = "find_user_by_id"
    FIND_USER_BY_NAME = "find_user_by_name"

    CREATE_WISH = "create_wish"
    UPDATE_WISH = "update_wish"
    DELETE_WISH = "delete_wish"
    GET_WISHLIST = "get_wishlist"
    FIND_WISH_BY_ID = "find_wish_by_id"

    CREATE_FRIEND = "create_friend"
    UPDATE_FRIEND = "update_friend"
    DELETE_FRIEND = "delete_friend"
    FIND_FRIEND_BY_ID = "find_friend_by_id"
    GET_FRIENDS_LIST = "get_friends_list"


class QueryRegistry:
    def __init__(self, queries_registry_directory: str):
        self.queries_registry_directory = queries_registry_directory
        self._queries: dict[SqlQuery, str] = {}
        self._load_all_queries()

    def _load_all_queries(self):
        for query_name in SqlQuery:
            filename = os.path.join(self.queries_registry_directory, f"{query_name}.sql")
            with open(filename) as query_file:
                query = query_file.read()
                query_id = SqlQuery(query_name)
                self._queries[query_id] = query

    def get_query(self, query: SqlQuery):
        return self._queries[query]
