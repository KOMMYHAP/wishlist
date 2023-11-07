import argparse
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    filters, ConversationHandler, PersistenceInput,

)

from data_types import User, WishlistRecord
from storage_interface import BaseStorage
from storage_local import LocalStorage

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger("wishlist_logger")
log.setLevel(logging.DEBUG)

WISH_TITLE, WISH_REFERENCE = range(2)
storage: BaseStorage | None = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.debug("'Start' command handler: "
              f"userid = '{update.effective_user.id}', "
              f"username = '{update.effective_user.username}'")

    user = User(update.effective_user.id, update.effective_user.username)
    new_user_created = await storage.create_user(user)
    if new_user_created:
        log.debug(f"New user: userid = '{update.effective_user.id}', ")

    await update.message.reply_text(f'Привет, {update.effective_user.username}!')


async def get_wishlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    wishlist_target_id = update.effective_user.id
    wishlist_target_name = update.effective_user.name
    if len(context.args) > 0:
        target_username = context.args[0]
        target_user = await storage.get_user_by_name(target_username)

        log.debug(f"User {update.effective_user.username} trying to get wishlist of user {target_username}")
        if target_user is None:
            await update.message.reply_text(f"Похоже, что '{target_username}' еще не знает обо мне")
            return

        if target_user.id != update.effective_user.id:
            wishlist_target_id = target_user.id
            wishlist_target_name = target_user.name

    is_external_request = wishlist_target_id != update.effective_user.id

    wishlist = await storage.get_wishlist(wishlist_target_id)
    wish_str_list = []

    for wish_idx in range(0, len(wishlist)):
        wish = wishlist[wish_idx]
        if wish.performed:
            continue

        wish_str = f"{wish_idx + 1}. {wish.title}"
        if is_external_request:
            if wish.reserved_by_user is not None:
                reserved_by_user = await storage.get_user_by_id(wish.reserved_by_user)
                wish_str += f" зарезервирован {reserved_by_user.name}"
        if len(wish.references) > 0:
            wish_str += ':\n' + '\n -'.join(wish.references)
        wish_str_list.append(wish_str)

    if len(wish_str_list) > 0:
        message = '\n'.join(wish_str_list)
    elif is_external_request:
        message = f"Вишлист пользователя '{wishlist_target_name}' пуст!"
    else:
        message = f"Вишлист пуст!"
    await update.message.reply_text(message)


async def try_complete_wish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if context.chat_data.get('temp_wish') is None:
        return False

    temp_wish = context.chat_data['temp_wish']
    wish_record = WishlistRecord(0, update.effective_user.id, temp_wish['title'], temp_wish['references'], None, False)
    await storage.create_wish(wish_record)
    return True


async def add_wish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await try_complete_wish(update, context)

    fast_wish_title = ' '.join(context.args)
    context.chat_data['temp_wish'] = {
        'title': fast_wish_title,
        'references': []
    }
    if len(fast_wish_title) > 0:
        await try_complete_wish(update, context)
        await update.message.reply_text(f"Я добавил новое желание в вишлист: {fast_wish_title}")
        return

    await update.message.reply_text(
        "Введи название того, что ты хочешь получить (/cancel, чтобы отменить)")
    return WISH_TITLE


async def wish_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data['temp_wish']['title'] = update.message.text
    await update.message.reply_text(
        "Записал. Еще желания? Если хочешь добавить ссылку, вводи /reference, либо /stop, чтобы вернуться в "
        "главное меню")
    return WISH_TITLE


async def wish_reference(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data['temp_wish']['references'].append(update.message.text)
    await update.message.reply_text(
        "Записал ссылку, можешь кидать еще. Введи /add, чтобы добавить новое желание, либо /stop, чтобы вернуться в "
        "главное меню")
    return WISH_REFERENCE


async def wish_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.chat_data.pop('temp_wish')
    await update.message.reply_text("Буду ждать новых желаний!")
    return ConversationHandler.END


async def remove_wish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("Пожалуйста, введи номер из вишлиста. Например, /remove 1")

    try:
        wish_idx = int(context.args[0]) - 1
    except ValueError:
        await update.message.reply_text("Пожалуйста, введи номер из вишлиста")
        return

    wishlist = await storage.get_wishlist(update.effective_user.id)
    if not (0 <= wish_idx < len(wishlist)):
        await update.message.reply_text(f"Пожалуйста, введи номер из вишлиста от 1 до {len(wishlist)}")
        return

    wish = wishlist[wish_idx]
    removed = await storage.remove_wish(update.effective_user.id, wish.wish_id)
    if not removed:
        await update.message.reply_text(f"Непредвиденная ошибка :(")

    await update.message.reply_text(f"Я пометил, что ты выполнил желание '{wish.title}'")


def main() -> None:
    parser = argparse.ArgumentParser("WishList telegram bot")
    parser.add_argument('-t', '--token', required=True)
    parser.add_argument('-s', '--storage-path', required=True)
    args = parser.parse_args()

    persistence = PicklePersistence(args.storage_path, PersistenceInput(True, False, True, False))

    global storage
    storage = LocalStorage(persistence)

    application = Application.builder().token(args.token).persistence(persistence).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("add", add_wish)],
        states={
            WISH_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, wish_title),
                CommandHandler('add', add_wish),
                CommandHandler('reference', wish_reference),
                CommandHandler('stop', wish_stop)
            ],
            WISH_REFERENCE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, wish_reference),
                CommandHandler('stop', wish_stop),
                CommandHandler('add', wish_title)
            ]
        },
        fallbacks=[CommandHandler("cancel", wish_stop)],
    ))
    application.add_handler(CommandHandler("get", get_wishlist))
    application.add_handler(CommandHandler("remove", remove_wish, has_args=True))

    application.run_polling()


if __name__ == '__main__':
    main()
