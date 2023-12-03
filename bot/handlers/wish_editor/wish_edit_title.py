from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.handlers.wish_editor.wish_editor_query import open_wish_editor_in_new_message
from wish.state_adapters.state_base_adapter import StateBaseAdapter
from wish.wish_manager import WishManager


async def wish_edit_title_handler(message: Message, bot: AsyncTeleBot, state: StateBaseAdapter, logger: Logger,
                                  wish_manager: WishManager) -> None:
    logger = logger.getChild('wish_edit_title')
    title = message.text.strip()
    if len(title) == 0:
        await bot.reply_to(message, 'Название должно содержать хотя бы один видимый символ!')
        return

    user_id = message.from_user.id
    wish_draft = await state.get_wish_editor_draft(user_id)
    if wish_draft is None:
        logger.error('Wish draft is required but was not created!')
        await bot.reply_to(message, 'Я не смог найти это желание, может попробуем с другим?')
        return

    wish_draft.title = title
    await state.update_wish_editor_draft(user_id, wish_draft)

    await open_wish_editor_in_new_message(bot, message, logger, wish_manager, wish_draft)
