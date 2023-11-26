from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.keyboards.wishlist_viewer_keyboard import generate_wishlist_viewer_keyboard
from wish.wish_manager import WishManager


async def show_wishlist_viewer(bot: AsyncTeleBot, message: Message, target_user_id: int, wish_manager: WishManager,
                               logger: Logger, page_idx: int) -> None:
    # logger = logger.getChild('show_wishlist_viewer')
    wishes_per_page = wish_manager.wish_per_page

    target_username = await wish_manager.find_username(target_user_id)
    if target_username is None:
        await bot.reply_to(message, f"Я не нашел такого пользователя :(")
        return

    # if user.username == target_username:
    #     logger.warning('Trying to show wishlist viewer for the same user %s!', target_username)
    #     await show_my_wishlist_editor(user, bot, wish_manager, page_idx)

    response = await wish_manager.get_wishlist(message.from_user.id, target_user_id)
    if response.owner is None:
        await bot.reply_to(message,
                           f"Я не нашел пользователя с именем '{target_username}'. Возможно, мы с ним еще не знакомы. Поделишься с ним ссылкой?")
        return

    text = f'Список желаний от {target_username}'
    if len(response.wishlist) == 0:
        text = '<желания не добавлены>'

    await bot.send_message(chat_id=message.chat.id,
                           text=text,
                           reply_markup=generate_wishlist_viewer_keyboard(response, target_user_id, page_idx,
                                                                          wishes_per_page))
