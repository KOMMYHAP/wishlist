from enum import Enum


class WishlistCommands(Enum):
    MY_WISHLIST = 'my_wishlist'
    USER_WISHLIST = 'user_wishlist'


def get_command_description(command: WishlistCommands):
    if command is WishlistCommands.MY_WISHLIST:
        return 'Список моих желаний'
    if command is WishlistCommands.USER_WISHLIST:
        return 'Список желаний другого пользователя'

    raise NotImplementedError()
