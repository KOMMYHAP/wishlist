from dataclasses import dataclass


@dataclass
class WishEditorDraft:
    editor_id: int
    title: str
    hint: str
    cost: str
    wish_id: int | None
