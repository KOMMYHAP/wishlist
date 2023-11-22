from logging import Logger

from telebot.asyncio_handler_backends import BaseMiddleware
from telebot.types import Message


class LoggerMiddleware(BaseMiddleware):

    def __init__(self, root_logger: Logger):
        super().__init__()
        self.update_types = ['message', 'callback_query']
        self._logger = root_logger

    async def pre_process(self, message: Message, data: dict):
        user_logger = self._logger.getChild(f'user {message.from_user.id}')
        data['logger'] = user_logger

    async def post_process(self, message, data, exception):
        pass
