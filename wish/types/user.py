from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    first_name: str | None
    last_name: str | None
    chat_id: int | None
