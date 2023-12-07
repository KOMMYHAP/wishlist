from bot.utilities.telegram_link import telegram_user_link
from wish.types.user import User


def get_user_fullname(user: User | None, fullname: bool = False, link: bool = False, username: bool = False) -> str:
    if not user:
        return "<unknown user>"

    if not link and not username:
        # enable at least one option
        if user.version == 0:
            # fullname is unavailable for 0 version
            fullname = False
            link = False
            username = True
        else:
            fullname = True

    _link = f"{telegram_user_link}{user.username}" if link else ""
    _username = f"@{user.username}" if username else ""
    _fullname = f"{user.first_name} {user.last_name}"

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
