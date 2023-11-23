from dataclasses import dataclass


@dataclass
class WishViewerDraft:
    editor_id: int
    viewer_id: int
    wish_id: int
    reserved: bool
