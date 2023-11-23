from dataclasses import dataclass


@dataclass
class WishEditorDraft:
    editor_id: int
    title: str
    hint: str
    cost: float
    wish_id: int | None
