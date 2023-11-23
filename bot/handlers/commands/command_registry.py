from enum import Enum


class WishlistCommands(Enum):
    MY_WISHLIST = 'my_wishlist'


def get_command_description(command: WishlistCommands):
    if command is WishlistCommands.MY_WISHLIST:
        return 'Список моих желаний'

    raise NotImplementedError()
