from bot.handlers.command_registry import WishlistCommands

current_bot_version = 2

_update_message_footer = "Спасибо, что помогаете с тестированием бота!"

_update_message_1 = """Обновление 0.8
1. В вишлист добавлено отображение номера текущей страницы и общее количество страниц
2. Добавлена возможность удалять желание с последующим подтверждением
3. Добавлена возможность бронировать и снимать бронь с желания: "Планирую подарить" и "Передумал дарить" соответственно
4. Убрана возможность увидеть, кто забронировал желания из твоего вишлиста
5. Добавлена возможность увидеть, кто забронировал желание при просмотре вишлиста другого пользователя 
6. Добавлено версионирование и вывод сообщений о переходе на новую версию :)
"""

_update_message_2 = f"""Обновление 0.9
1. Добавлен функционал "друзей". 
1.1 Теперь пользователь, чей вишлист был просмотрен с помощью /{WishlistCommands.USER_WISHLIST.value}, будет добавлен в список друзей для быстрого доступа.
1.2 Список друзей сортируется по возрастанию в порядке общращения к вишлисту пользователя
1.3. Друзей можно удалять из списка
2. Добавлена возможность проверить наличие обновлений у друзей с помощью /{WishlistCommands.MY_WISHLIST.value}
3. Добавлен функционал миграции на новую версию
4. Скрыта возможность добавлять желания в вишлист другого пользователя
5. Учтены пользователи, у которых не задан @username и last name в настройках аккаунта.
"""

_todo_message = """TODO:
1. Антивишлист. В качестве временного решения можно добавить желание и попросить кого-нибудь забронить его.
2. Категории. Добавить возможность сгруппировать желания по категориям, например, "бытовая техника" или "книги". Нужно больше примеров, в идеале рефы на сторонние сервисы по вишлистам.
3. Автоматическое удаление неактуальных сообщений.
"""

_update_message_list = [
    _update_message_1,
    _update_message_2
]


def get_update_message(user_version: int) -> str | None:
    user_version = max(0, user_version)
    if user_version >= current_bot_version:
        return None
    return ("\n\n".join(_update_message_list[user_version:]) +
            "\n\n" + _todo_message +
            "\n\n" + _update_message_footer)
