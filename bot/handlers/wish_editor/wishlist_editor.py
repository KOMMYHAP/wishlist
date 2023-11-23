from telebot.async_telebot import AsyncTeleBot
from telebot.types import User

from bot.keyboards.wishlist_editor_keyboard import generate_wishlist_editor_keyboard
from wish.wish_manager import WishManager


async def show_my_wishlist_editor(user: User, bot: AsyncTeleBot,
                                  wish_manager: WishManager, page_idx: int) -> None:
    wishes_per_page = wish_manager.wish_per_page

    response = await wish_manager.get_wishlist(user.id, user.id)
    text = 'Список желаний'
    if len(response.wishlist) == 0:
        text = 'Список желаний пуст'

    await bot.send_message(chat_id=user.id,
                           text=text,
                           reply_markup=generate_wishlist_editor_keyboard(response, page_idx, wishes_per_page))
