from dataclasses import dataclass


@dataclass
class WishDraft:
    editor_id: int
    title: str
    hint: str
    references: list[str]
    cost: float
    wish_id: int | None
