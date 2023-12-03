from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.handlers.wish_editor.wish_editor_query import open_wish_editor_in_new_message
from bot.handlers.wish_editor.wishlist_editor import send_my_wishlist_editor
from wish.state_adapters.state_base_adapter import StateBaseAdapter
from wish.wish_manager import WishManager


async def wish_edit_deletion_handler(message: Message, bot: AsyncTeleBot, state: StateBaseAdapter, logger: Logger,
                                     wish_manager: WishManager) -> None:
    logger = logger.getChild('wish_edit_deletion')
    title = message.text
    user_id = message.from_user.id
    wish_draft = await state.get_wish_editor_draft(user_id)
    if wish_draft is None:
        logger.error('Wish draft is required but was not created!')
        await bot.reply_to(message, 'Я не смог найти это желание, может попробуем с другим?')
        return

    if wish_draft.title == title:
        await state.delete_wish_editor_draft(user_id)
        if wish_draft.wish_id is not None:
            await wish_manager.remove_wish(user_id, wish_draft.wish_id)
        await send_my_wishlist_editor(logger, message, bot, wish_manager, 0)
    else:
        await open_wish_editor_in_new_message(bot, message, logger, wish_manager, wish_draft)
