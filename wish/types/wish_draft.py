from dataclasses import dataclass


@dataclass
class WishDraft:
    editor_id: int
    title: str
    references: list[str]
    wish_id: int | None
