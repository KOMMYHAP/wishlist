from dataclasses import dataclass


@dataclass
class WishDraft:
    title: str
    references: list[str]
    wish_id: int | None
