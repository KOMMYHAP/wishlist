from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    first_name: str
    last_name: str
    chat_id: int
