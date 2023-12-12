import asyncio
from asyncio import WindowsSelectorEventLoopPolicy

from bot.telegram_bot import entry_point

if __name__ == '__main__':
    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    asyncio.run(entry_point())
