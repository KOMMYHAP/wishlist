from dataclasses import dataclass

from bot.handlers.command_registry import WishlistCommands


@dataclass
class VersionUpdateInfo:
    version: int
    human_readable_version: str
    message: str


def get_current_version_info() -> VersionUpdateInfo:
    return next((info for info in _update_list if info.version == _current_bot_version),
                VersionUpdateInfo(_current_bot_version, '', ''))


def get_current_version() -> int:
    return _current_bot_version


def get_update_message(user_version: int) -> str | None:
    user_version = max(0, user_version)
    if user_version >= get_current_version():
        return None

    version_updated_info = (info for info in _update_list if info.version > user_version)
    non_empty_update_info = (info for info in version_updated_info if len(info.message) > 0)
    update_messages = (f'Обновление {info.human_readable_version}\n{info.message}' for info in non_empty_update_info)
    return ("\n\n".join(update_messages) +
            "\n" + _update_message_footer)


_current_bot_version = 6

_update_message_1 = \
    """1. В вишлист добавлено отображение номера текущей страницы и общее количество страниц
2. Добавлена возможность удалять желание с последующим подтверждением
3. Добавлена возможность бронировать и снимать бронь с желания: "Планирую подарить" и "Передумал дарить" соответственно
4. Убрана возможность увидеть, кто забронировал желания из твоего вишлиста
5. Добавлена возможность увидеть, кто забронировал желание при просмотре вишлиста другого пользователя 
6. Добавлено версионирование и вывод сообщений о переходе на новую версию :)
"""

_update_message_2 = \
    f"""1. Добавлен функционал "друзей". 
1.1 Теперь пользователь, чей вишлист был просмотрен с помощью /{WishlistCommands.USER_WISHLIST.value}, будет добавлен в список друзей для быстрого доступа.
1.2 Список друзей сортируется по возрастанию в порядке общращения к вишлисту пользователя
1.3. Друзей можно удалять из списка
2. Добавлена возможность проверить наличие обновлений у друзей с помощью /{WishlistCommands.MY_WISHLIST.value}
3. Добавлен функционал миграции на новую версию
4. Скрыта возможность добавлять желания в вишлист другого пользователя
5. Учтены пользователи, у которых не задан @username и last name в настройках аккаунта.
"""

_update_message_3 = \
    f"""1. Исправлено отображение имен некоторых пользователей в списке друзей
2. Добавлен функционал пролистывания списка друзей
"""

_update_message_4 = \
    f"""1. Данные всех пользователей успешно мигрировали в PostgreSQL
2. Добавлена команда /{WishlistCommands.ABOUT.value}
"""

_update_message_6 = f""" Добавлена возможность поделиться своим вишлистом (см. подробнее в /{WishlistCommands.ABOUT.value})"""

_update_message_minor_changes = 'Исправлены некоторые ошибки, улучшено взаимодействие с пользователем'
_update_message_footer = 'Спасибо, что пользуешься этим ботом!'

_update_list = [
    VersionUpdateInfo(1, '0.8', _update_message_1),
    VersionUpdateInfo(2, '0.9', _update_message_2),
    VersionUpdateInfo(3, '0.9.1', _update_message_3),
    VersionUpdateInfo(4, '0.9.2', _update_message_4),
    VersionUpdateInfo(5, '0.9.3', _update_message_minor_changes),
    VersionUpdateInfo(6, '0.9.4', _update_message_6),
]
