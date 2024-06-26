from logging import Logger

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from bot.filters.wish_view_action_filter import wish_view_action_callback_data
from bot.handlers.bot_idle_state import bot_idle_state
from bot.handlers.wish_viewer.wish_viewer_draft import WishViewerDraft
from bot.handlers.wish_viewer.wish_viewer_states import WishViewerStates
from bot.handlers.wish_viewer.wishlist_viewer import edit_user_wishlist_viewer
from wish.state_adapters.state_base_adapter import StateBaseAdapter
from wish.types.wish_record import WishRecord
from wish.wish_manager import WishManager


async def wish_view_action_query(call: CallbackQuery, bot: AsyncTeleBot, wish_manager: WishManager,
                                 state: StateBaseAdapter, logger: Logger) -> None:
    logger = logger.getChild('wish_view_action_query')

    callback_data: dict = wish_view_action_callback_data.parse(callback_data=call.data)
    action = int(callback_data['action'])
    editor_id = int(callback_data['editor_id'])

    await bot.answer_callback_query(call.id)

    draft = await state.get_wish_viewer_draft(call.from_user.id)
    if draft is None:
        await bot.send_message(call.message.chat.id, 'Извини, но не мог бы ты повторно выбрать желание?')
        return

    if draft.editor_id != editor_id:
        await bot.send_message(call.message.chat.id,
                               'Пожалуйста, используй кнопки с последнего открытого окна просмотра!')
        return

    wish = await wish_manager.get_wish(draft.wish_id)
    if wish is None:
        logger.error('Wish draft is missing, nothing to apply!')
        await bot.send_message(call.message.chat.id, 'Что-то пошло не так, не мог бы ты попробовать снова?')
        return

    if action == WishViewerStates.RESERVATION:
        await _wish_viewer_reserve(call, bot, wish_manager, state, logger, draft, wish)
    elif action == WishViewerStates.BACK:
        await _wish_viewer_back(call, bot, wish_manager, state, wish.owner_id, logger)
    else:
        await bot.send_message(call.message.chat.id, 'Извини, но кажется я тебя не понял')


async def _wish_viewer_reserve(call: CallbackQuery, bot: AsyncTeleBot, wish_manager: WishManager,
                               state: StateBaseAdapter, logger: Logger, draft: WishViewerDraft, wish: WishRecord):
    logger = logger.getChild('wish_viewer_reserve')

    error_message: str | None = None

    if wish.reserved_by_user_id and wish.reserved_by_user_id != call.from_user.id:
        error_message = "Упс, кажется кто-то другой тоже хочет исполнить это желание!"

    if wish.owner_id == call.from_user.id:
        error_message = "Позволь твоим друзьям исполнить твое желание :)"

    if error_message is not None:
        await bot.send_message(call.message.chat.id, error_message)
        await edit_user_wishlist_viewer(bot, logger, call, wish.owner_id, wish_manager, 0)
        return

    if wish.reserved_by_user_id is None:
        draft.reserved = True
    else:
        draft.reserved = False

    await wish_manager.update_wish_by_viewer(call.from_user.id, draft)
    await state.delete_wish_viewer_draft(call.from_user.id)

    # todo: store open page id when user starts to edit wish and restore it here
    await edit_user_wishlist_viewer(bot, logger, call, wish.owner_id, wish_manager, 0)


async def _wish_viewer_back(call: CallbackQuery, bot: AsyncTeleBot, wish_manager: WishManager,
                            state: StateBaseAdapter, wish_owner_id: int, logger: Logger) -> None:
    logger = logger.getChild('wish_viewer_back')
    await bot.set_state(call.from_user.id, bot_idle_state)
    await state.delete_wish_viewer_draft(call.from_user.id)

    # todo: store open page id when user starts to edit wish and restore it here
    await edit_user_wishlist_viewer(bot, logger, call, wish_owner_id, wish_manager, 0)
