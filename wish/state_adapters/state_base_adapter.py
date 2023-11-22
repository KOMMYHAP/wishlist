from abc import ABC, abstractmethod

from wish.types.wish_draft import WishDraft


class StateBaseAdapter(ABC):
    @abstractmethod
    async def get_wish_draft(self, user_id: int) -> WishDraft | None:
        raise NotImplementedError

    @abstractmethod
    async def update_wish_draft(self, user_id: int, wish_draft: WishDraft) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def delete_wish_draft(self, user_id: int) -> bool:
        raise NotImplementedError
