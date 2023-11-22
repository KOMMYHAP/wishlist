from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from bot.filters.wish_edit_action_filter import wish_edit_action_callback_data
from bot.handlers.wishlist_get import show_wishlist
from bot.types.wish_edit_states import WishEditStates
from wish.state_adapters.state_base_adapter import StateBaseAdapter
from wish.wish_manager import WishManager


async def wish_edit_action_query(call: CallbackQuery, bot: AsyncTeleBot, wish_manager: WishManager,
                                 state: StateBaseAdapter, logger: Logger) -> None:
    logger = logger.getChild('wish_edit_action_query')

    callback_data: dict = wish_edit_action_callback_data.parse(callback_data=call.data)
    action = int(callback_data['action'])

    reply_text_dict = {
        WishEditStates.REFERENCES.value: 'Введи ссылку',
        WishEditStates.TITLE.value: 'Введи название',
        WishEditStates.COMPLETION.value: '',
        WishEditStates.ABORT.value: '',
    }

    action_data = reply_text_dict.get(action)
    if action_data is None:
        raise NotImplementedError

    await bot.set_state(call.from_user.id, action)
    await bot.answer_callback_query(call.id)

    if action == WishEditStates.COMPLETION:
        await _wish_apply(call, bot, wish_manager, state, logger)
    elif action == WishEditStates.ABORT:
        await _wish_abort(call, bot, wish_manager, state)
    else:
        await bot.send_message(call.message.chat.id, action_data)


async def _wish_apply(call: CallbackQuery, bot: AsyncTeleBot, wish_manager: WishManager,
                      state: StateBaseAdapter, logger: Logger):
    logger = logger.getChild('wish_apply_editing')
    wish_draft = await state.get_wish_draft(call.from_user.id)
    if wish_draft is None:
        logger.error('Wish draft is missing, nothing to apply!')
        raise NotImplementedError

    if wish_draft.wish_id is None:
        await wish_manager.create_wish(call.from_user.id, wish_draft)
    else:
        await wish_manager.update_wish(call.from_user.id, wish_draft)

    await state.delete_wish_draft(call.from_user.id)

    # todo: store open page id when user starts to edit wish and restore it here
    await show_wishlist(call.from_user, bot, wish_manager, 0)


async def _wish_abort(call: CallbackQuery, bot: AsyncTeleBot, wish_manager: WishManager,
                      state: StateBaseAdapter) -> None:
    await bot.delete_state(call.from_user.id)
    await state.delete_wish_draft(call.from_user.id)
    # todo: store open page id when user starts to edit wish and restore it here
    await show_wishlist(call.from_user, bot, wish_manager, 0)
