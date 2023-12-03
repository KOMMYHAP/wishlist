from dataclasses import dataclass

current_user_data_version = 1


@dataclass
class User:
    version: int
    id: int
    username: str
    first_name: str
    last_name: str
    chat_id: int
