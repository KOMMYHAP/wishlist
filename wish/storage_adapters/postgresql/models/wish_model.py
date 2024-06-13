from pydantic import BaseModel


class WishModel(BaseModel):
    wish_id: int
    owner_id: int
    title: str
    hint: str
    cost: str
    reserved_by_user_id: int | None
