from telebot.async_telebot import AsyncTeleBot

from bot.filters.wish_creator_filter import WishCreatorCallbackFilter
from bot.filters.wish_edit_action_filter import WishEditActionCallbackFilter
from bot.filters.wish_editor_query_filter import WishEditorCallbackFilter
from bot.filters.wish_state_filter import WishStateFilter
from bot.filters.wish_view_action_filter import WishViewActionCallbackFilter
from bot.filters.wish_viewer_query_filter import WishViewerCallbackFilter
from bot.filters.wishlist_editor_filter import WishlistEditorCallbackFilter
from bot.filters.wishlist_viewer_filter import WishlistViewerCallbackFilter


def setup_filters(bot: AsyncTeleBot) -> None:
    bot.add_custom_filter(WishlistViewerCallbackFilter())
    bot.add_custom_filter(WishlistEditorCallbackFilter())
    bot.add_custom_filter(WishEditActionCallbackFilter())
    bot.add_custom_filter(WishViewActionCallbackFilter())
    bot.add_custom_filter(WishEditorCallbackFilter())
    bot.add_custom_filter(WishViewerCallbackFilter())
    bot.add_custom_filter(WishCreatorCallbackFilter())
    bot.add_custom_filter(WishStateFilter(bot))
