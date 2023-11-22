from telebot.async_telebot import AsyncTeleBot

from bot.filters.wish_creator_filter import WishCreatorCallbackFilter
from bot.filters.wish_edit_action_filter import WishEditActionCallbackFilter
from bot.filters.wish_editor_query_filter import WishEditorCallbackFilter
from bot.filters.wish_none_filter import WishNoneCallbackFilter
from bot.filters.wish_state_filter import WishStateFilter
from bot.filters.wishlist_filter import WishlistCallbackFilter


def setup_filters(bot: AsyncTeleBot) -> None:
    bot.add_custom_filter(WishlistCallbackFilter())
    bot.add_custom_filter(WishEditActionCallbackFilter())
    bot.add_custom_filter(WishEditorCallbackFilter())
    bot.add_custom_filter(WishCreatorCallbackFilter())
    bot.add_custom_filter(WishNoneCallbackFilter())
    bot.add_custom_filter(WishStateFilter(bot))
