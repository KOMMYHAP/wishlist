import argparse
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    filters, ConversationHandler,

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

admin_password = None

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

    message = f'Привет, {update.effective_user.username}!'

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def get_wishlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    wishlist = await storage.get_wishlist(update.effective_user.id)
    wish_str_list = []

    for wish_idx in range(0, len(wishlist)):
        wish = wishlist[wish_idx]
        wish_str = f"{wish_idx + 1}. {wish.title}"
        if wish.reserved_by_user is not None and wish.reserved_by_user != update.effective_user.id:
            reserved_by_user = await storage.get_user_by_id(wish.reserved_by_user)
            wish_str += f" reserved by {reserved_by_user.name}"
        if len(wish.references) > 0:
            wish_str += ':\n' + '\n -'.join(wish.references)
        wish_str_list.append(wish_str)

    message = 'Кажется твой вишлист пуст'
    if len(wish_str_list) > 0:
        message = '\n'.join(wish_str_list)
    await update.message.reply_text(message)


async def add_wish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['temp_wish'] = {
        'title': '',
        'references': []
    }
    await update.message.reply_text("Введи название того, что ты хочешь получить")
    return WISH_TITLE


async def wish_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['temp_wish']['title'] = update.message.text
    await update.message.reply_text("Если у тебя есть ссылки на примеры, могу записать (/skip, чтобы пропустить)")
    return WISH_REFERENCE


async def wish_reference(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    references = context.user_data['temp_wish']['references']
    references.append(update.message.text)
    await update.message.reply_text("Кидай еще, если есть (/skip, если хватит)")
    return WISH_REFERENCE


async def wish_skip_references(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    temp_wish = context.user_data.pop('temp_wish')
    wish_record = WishlistRecord(0, update.effective_user.id, temp_wish['title'], temp_wish['references'], None, False)
    await storage.create_wish(wish_record)
    return ConversationHandler.END


async def wish_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop('temp_wish')
    await update.message.reply_text("Буду ждать")
    return ConversationHandler.END


def main() -> None:
    parser = argparse.ArgumentParser("WishList telegram bot")
    parser.add_argument('-t', '--token', required=True)
    parser.add_argument('-p', '--admin-password', required=False)
    parser.add_argument('-s', '--storage-path', required=True)
    args = parser.parse_args()

    global admin_password
    admin_password = args.admin_password

    persistence = PicklePersistence(args.storage_path)

    global storage
    storage = LocalStorage(persistence)

    application = Application.builder().token(args.token).persistence(persistence).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("add", add_wish)],
        states={
            WISH_TITLE: [MessageHandler(filters.TEXT, wish_title)],
            WISH_REFERENCE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, wish_reference),
                CommandHandler('skip', wish_skip_references)
            ]
        },

        fallbacks=[CommandHandler("cancel", wish_cancel)],
    ))
    application.add_handler(CommandHandler("get", get_wishlist))

    application.run_polling()


if __name__ == '__main__':
    main()
