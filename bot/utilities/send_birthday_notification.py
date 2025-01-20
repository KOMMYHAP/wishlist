import argparse
import asyncio
from asyncio import WindowsSelectorEventLoopPolicy

from telebot.async_telebot import AsyncTeleBot

_birthday_message = """Привет!
Кажется твой вишлист уже давненько не обновлялся, а ведь у тебя скоро день рождения...
Давай поможем твоим друзьям выбрать действительно желанный подарок!
Ведь все хотят быть осликом Иа и получить свой "шнурок")
"""


async def send_birthday_notification(bot: AsyncTeleBot, user_id: int) -> None:
    # chat_id is the same as user_id in private messages
    chat_id = user_id
    await bot.send_message(chat_id, _birthday_message)


async def _notification_sender_entry_point() -> None:
    parser = argparse.ArgumentParser("WishList Notification Sender")
    parser.add_argument('-t', '--token', required=True)
    parser.add_argument('-i', '--user_id', required=True)
    args = parser.parse_args()

    bot = AsyncTeleBot(args.token)
    await send_birthday_notification(bot, args.user_id)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    asyncio.run(_notification_sender_entry_point())
