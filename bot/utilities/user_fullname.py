from wish.types.user import User


def get_user_fullname(user: User | None) -> str:
    if user:
        return f"{user.first_name} {user.last_name} (@{user.username})"
    return "<unknown user>"
