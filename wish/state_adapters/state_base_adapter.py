from abc import ABC, abstractmethod

from bot.handlers.wish_editor.wish_editor_draft import WishEditorDraft
from bot.handlers.wish_viewer.wish_viewer_draft import WishViewerDraft


class StateBaseAdapter(ABC):
    @abstractmethod
    async def get_wish_editor_draft(self, user_id: int) -> WishEditorDraft | None:
        raise NotImplementedError

    @abstractmethod
    async def update_wish_editor_draft(self, user_id: int, draft: WishEditorDraft) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def delete_wish_editor_draft(self, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_wish_viewer_draft(self, user_id: int) -> WishViewerDraft | None:
        raise NotImplementedError

    @abstractmethod
    async def update_wish_viewer_draft(self, user_id: int, draft: WishViewerDraft) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def delete_wish_viewer_draft(self, user_id: int) -> bool:
        raise NotImplementedError
