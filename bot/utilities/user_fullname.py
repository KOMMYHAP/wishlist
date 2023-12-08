from bot.utilities.telegram_link import telegram_user_link
from wish.types.user import User


def get_user_fullname(user: User | None, fullname: bool = False, link: bool = False, username: bool = False) -> str:
    if not user:
        return "<unknown user>"

    if len(user.username) == 0:
        link = False
        username = False

    if not link and not username:
        fullname = True

    if link and username:
        username = True

    if user.version == 0:
        fullname = True
        link = False
        username = False

    _link = f"{telegram_user_link}{user.username}" if link else ""
    _username = f"@{user.username}" if username else ""
    if user.first_name and len(user.last_name) > 0:
        _fullname = f"{user.first_name} {user.last_name}"
    else:
        _fullname = f"{user.first_name}"

    if fullname:
        if link:
            return f"{_fullname} ({_link})"
        if username:
            return f"{_fullname} ({_username})"
    if link:
        return f"{_link}"
    if username:
        return f"{_username}"

    return _fullname
