from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.handlers.wish_editor_query import open_wish_editor_in_new_message
from wish.state_adapters.state_base_adapter import StateBaseAdapter


async def wish_edit_reference_handler(message: Message, bot: AsyncTeleBot,
                                      state: StateBaseAdapter, logger: Logger) -> None:
    logger = logger.getChild('wish_edit_reference')
    reference = message.text.strip()
    if len(reference) == 0:
        await bot.reply_to(message, 'Ссылка должна содержать хотя бы один видимый символ! Попробуй еще раз')
        return

    user_id = message.from_user.id
    wish_draft = await state.get_wish_draft(user_id)
    if wish_draft is None:
        logger.error('Wish draft is required but was not created!')
        await bot.reply_to(message, 'Ой, кажется я сломался')
        return

    wish_draft.references = reference.split('\n')
    await state.update_wish_draft(user_id, wish_draft)

    await open_wish_editor_in_new_message(message, bot, state, logger)
