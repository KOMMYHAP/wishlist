from enum import Enum


class WishlistCommands(Enum):
    MY_WISHLIST = 'my_wishlist'
    USER_WISHLIST = 'user_wishlist'
    GET_UPDATES = 'get_updates'
    ABOUT = 'about'


def get_command_description(command: WishlistCommands):
    if command is WishlistCommands.MY_WISHLIST:
        return 'Список моих желаний'
    if command is WishlistCommands.USER_WISHLIST:
        return 'Список желаний другого пользователя'
    if command is WishlistCommands.GET_UPDATES:
        return 'Проверить обновления желаний у других пользователей'
    if command is WishlistCommands.ABOUT:
        return 'Обо мне'

    raise NotImplementedError()
