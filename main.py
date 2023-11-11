import asyncio
import logging

from bot.telegram_bot import entry_point

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

if __name__ == '__main__':
    asyncio.run(entry_point())
