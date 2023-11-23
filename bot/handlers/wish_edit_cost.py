from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from bot.handlers.wish_editor_query import open_wish_editor_in_new_message
from wish.state_adapters.state_base_adapter import StateBaseAdapter


async def wish_edit_cost_handler(message: Message, bot: AsyncTeleBot, state: StateBaseAdapter, logger: Logger) -> None:
    logger = logger.getChild('wish_edit_cost')
    cost_message = message.text.strip()

    try:
        cost = float(cost_message)
    except ValueError:
        await bot.reply_to(message, 'Я не смог понять стоимость подарка, не мог бы ты попробовать еще разок?')
        return

    if not cost.is_integer():
        await bot.reply_to(message, 'Не похоже на настоящую стоимость...')
        return

    user_id = message.from_user.id
    wish_draft = await state.get_wish_draft(user_id)
    if wish_draft is None:
        logger.error('Wish draft is required but was not created!')
        await bot.reply_to(message, 'Я не смог найти это желание, может попробуем с другим?')
        return

    wish_draft.cost = cost
    await state.update_wish_draft(user_id, wish_draft)
    await open_wish_editor_in_new_message(message, bot, wish_draft)
