import logging

from telebot.async_telebot import ExceptionHandler


class DebugExceptionHandler(ExceptionHandler):

    def __init__(self):
        self._logger = logging.getLogger('exceptions')

    def handle(self, exception):
        self._logger.exception('Exception occurred! ', exc_info=exception)
        return False
