from telebot.asyncio_handler_backends import BaseMiddleware

from wish.state_adapters.state_base_adapter import StateBaseAdapter


class StateAdapterMiddleware(BaseMiddleware):
    def __init__(self, state_adapter: StateBaseAdapter):
        super().__init__()
        self._state_adapter = state_adapter
        self.update_types = ['message', 'callback_query']

    async def pre_process(self, message, data):
        data['state'] = self._state_adapter

    async def post_process(self, message, data, exception):
        pass
