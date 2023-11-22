from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, User

from bot.filters.wishlist_filter import wishlist_callback_data
from bot.keyboards.wishlist_keyboard import generate_wishlist_keyboard
from wish.wish_manager import WishManager


async def wishlist_get(call: CallbackQuery, bot: AsyncTeleBot, wish_manager: WishManager) -> None:
    callback_data: dict = wishlist_callback_data.parse(callback_data=call.data)
    page_idx = int(callback_data['page_idx'])
    await show_wishlist(call.from_user, bot, wish_manager, page_idx)


async def show_wishlist(user: User, bot: AsyncTeleBot,
                        wish_manager: WishManager, page_idx: int | None) -> None:
    if page_idx is None:
        page_idx = 0

    wishes_per_page = wish_manager.wish_per_page

    response = await wish_manager.get_wishlist(user.id, user.username)
    text = 'Список желаний'
    if len(response.wishlist) == 0:
        text = 'Список желаний пуст'

    await bot.send_message(chat_id=user.id,
                           text=text,
                           reply_markup=generate_wishlist_keyboard(response, page_idx, wishes_per_page))
