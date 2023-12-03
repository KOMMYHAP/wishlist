from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.keyboards.wishlist_editor_keyboard import generate_wishlist_editor_keyboard
from wish.wish_manager import WishManager


async def send_my_wishlist_editor(message: Message, bot: AsyncTeleBot, wish_manager: WishManager,
                                  page_idx: int) -> None:
    return await _send_my_wishlist_editor_impl(bot, message, message.from_user.id, wish_manager, page_idx)


async def edit_my_wishlist_editor(message: Message, user_id: int, bot: AsyncTeleBot, wish_manager: WishManager,
                                  page_idx: int) -> None:
    return await _send_my_wishlist_editor_impl(bot, message, user_id, wish_manager, page_idx)


async def _send_my_wishlist_editor_impl(bot: AsyncTeleBot, message: Message, user_id: int, wish_manager: WishManager,
                                        page_idx: int) -> None:
    wishes_per_page = wish_manager.wish_per_page
    response = await wish_manager.get_wishlist(user_id, user_id)
    pages_count = len(response.wishlist) / wish_manager.wish_per_page

    text = 'Список желаний'
    if len(response.wishlist) == 0:
        text = 'Список желаний пуст'
    elif pages_count > 1:
        text += f"(стр. {page_idx + 1}/{pages_count})"

    await bot.edit_message_text(text, message.chat.id, message.id,
                                reply_markup=generate_wishlist_editor_keyboard(response, page_idx, wishes_per_page))
