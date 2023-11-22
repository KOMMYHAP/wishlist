from telebot.asyncio_handler_backends import BaseMiddleware

from wish.wish_manager import WishManager


class WishMiddleware(BaseMiddleware):
    def __init__(self, wish_manager: WishManager):
        super().__init__()
        self._wish_manager = wish_manager
        self.update_types = ['message', 'callback_query']

    async def pre_process(self, message, data):
        data['wish_manager'] = self._wish_manager

    async def post_process(self, message, data, exception):
        pass
