from bot.handlers.command_registry import WishlistCommands

current_version = 2

update_message_header = ""
update_message_footer = "Спасибо, что помогаете с тестированием бота!"

update_message_1 = """Обновление 0.8
1. В вишлист добавлено отображение номера текущей страницы и общее количество страниц
2. Добавлена возможность удалять желание с последующим подтверждением
3. Добавлена возможность бронировать и снимать бронь с желания: "Планирую подарить" и "Передумал дарить" соответственно
4. Убрана возможность увидеть, кто забронировал желания из твоего вишлиста
5. Добавлена возможность увидеть, кто забронировал желание при просмотре вишлиста другого пользователя 
6. Добавлено версионирование и вывод сообщений о переходе на новую версию :)
"""

update_message_2 = f"""Обновление 0.9
1. Добавлен функционал "друзей". 
1.1 Теперь пользователь, чей вишлист был просмотрел с помощью /{WishlistCommands.USER_WISHLIST.value} будет добавлен в список друзей для быстрого доступа.
1.2 Список друзей сортируется по возрастанию в порядке общращения к вишлисту пользователя
1.3. Друзей можно удалять из списка
2. Добавлена возможность проверить наличие обновлений у друзей с помощью /{WishlistCommands.MY_WISHLIST.value}
"""

update_message_list = [
    update_message_1,
    update_message_2
]


def get_update_message(user_version: int) -> str | None:
    user_version = max(0, user_version)
    if user_version >= current_version:
        return None
    return (f"{update_message_header}\n\n" +
            "\n\n".join(update_message_list[user_version:]) +
            f"\n\n{update_message_footer}")
