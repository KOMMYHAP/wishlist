from telebot.async_telebot import AsyncTeleBot
from telebot.types import BotCommand, Message

from bot.handlers.command_registry import WishlistCommands, get_command_description
from bot.handlers.wishlist_get import show_wishlist
from wish.types.user import User
from wish.wish_manager import WishManager


async def command_start_handler(message: Message, bot: AsyncTeleBot, wish_manager: WishManager) -> None:
    user = User(message.from_user.id, message.from_user.username)

    bot_commands: list[BotCommand] = []
    for wishlist_command in WishlistCommands:
        bot_commands.append(
            BotCommand(command=wishlist_command.value, description=get_command_description(wishlist_command)))
    await bot.set_my_commands(bot_commands)

    new_user_created = await wish_manager.register_user(user)
    if new_user_created:
        await bot.send_message(message.chat.id, f'Привет, {user.name}!')
    await show_wishlist(message.from_user, bot, wish_manager, 0)
