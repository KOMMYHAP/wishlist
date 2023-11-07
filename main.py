import argparse
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    filters,
    ConversationHandler,
    PersistenceInput
)

from data_types import User
from storage_local import LocalStorage
from wish_manager import WishManager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger("bot_api")
log.setLevel(logging.DEBUG)

WISH_TITLE, WISH_REFERENCE = range(2)
wish_manager: WishManager | None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = User(update.effective_user.id, update.effective_user.name)
    await wish_manager.register_user(user)
    await update.message.reply_text(f'Привет, {update.effective_user.name}!')


async def get_wishlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    wishlist_target_name = update.effective_user.name
    if len(context.args) > 0:
        wishlist_target_name = context.args[0]

    response = await wish_manager.get_wishlist(update.effective_user.id, wishlist_target_name)
    if response.owner is None:
        await update.message.reply_text(f"Я не смог найти пользователя с именем '{wishlist_target_name}'. "
                                        "Может быть он еще не знает обо мне?")
        return

    is_external_request = response.owner.id != update.effective_user.id

    wishlist = response.wishlist
    wish_str_list = []

    for wish_idx in range(0, len(wishlist)):
        wish = wishlist[wish_idx]
        if wish.performed:
            continue

        wish_str = f"{wish_idx + 1}. {wish.title}"
        if is_external_request:
            reserved_by_user = response.reservation_map.get(wish.wish_id)
            if reserved_by_user is not None:
                wish_str += f" зарезервирован за '{reserved_by_user.name}'"
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


async def add_wish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    fast_wish_title = ' '.join(context.args).strip()
    if len(fast_wish_title) > 0:
        await wish_manager.add_wish_title(update.effective_user.id, fast_wish_title)
        await update.message.reply_text(f"Я добавил новое желание в вишлист: '{fast_wish_title}'")
        return

    await update.message.reply_text(
        "Введи название того, что ты хочешь получить (/cancel, чтобы отменить)")
    return WISH_TITLE


async def wish_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    title = update.message.text.strip()
    if len(title) > 0:
        await wish_manager.add_wish_title(update.effective_user.id, update.message.text)
        await update.message.reply_text(
            "Записал. Еще желания? Если хочешь добавить ссылку, вводи /reference, либо /stop, чтобы вернуться в "
            "главное меню")
    else:
        await update.message.reply_text(
            "Введи название того, что ты хочешь получить. "
            "Если хочешь добавить ссылку, вводи /reference, либо /stop, чтобы вернуться в главное меню")
    return WISH_TITLE


async def wish_reference(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reference = update.message.text.strip()
    if len(reference) > 0:
        await wish_manager.add_wish_reference(update.effective_user.id, update.message.text.strip())
        await update.message.reply_text(
            "Записал ссылку, можешь кидать еще. "
            "Введи /add, чтобы добавить новое желание, либо /stop, чтобы вернуться в главное меню")
    else:
        await update.message.reply_text(
            "Введи ссылку, чтобы я мог прикрепить её к твоему желанию. "
            "Введи /add, чтобы добавить новое желание, либо /stop, чтобы вернуться в главное меню")
    return WISH_REFERENCE


async def wish_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await wish_manager.remove_incomplete_wish(update.effective_user.id)
    await update.message.reply_text("Буду ждать новых желаний!")
    return ConversationHandler.END


async def remove_wish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        log.debug('remove_wish(%d) no args', update.effective_user.id)
        await update.message.reply_text("Пожалуйста, введи номер из вишлиста. Например, /remove 1")

    try:
        wish_idx = int(context.args[0]) - 1
    except ValueError:
        log.debug(f'remove_wish({update.effective_user.id}) invalid arg')
        await update.message.reply_text("Пожалуйста, введи номер из вишлиста")
        return

    removed = await wish_manager.remove_wish(update.effective_user.id, wish_idx)
    if not removed:
        await update.message.reply_text(f"Я не смог удалить твое желание. Пожалуйста, проверь правильность ввода")

    await update.message.reply_text(f"Я пометил, что ты выполнил желание")


def main() -> None:
    parser = argparse.ArgumentParser("WishList telegram bot")
    parser.add_argument('-t', '--token', required=True)
    parser.add_argument('-s', '--storage-path', required=True)
    args = parser.parse_args()

    persistent_bot_and_user_data = PersistenceInput(True, False, True, False)
    persistence = PicklePersistence(args.storage_path, persistent_bot_and_user_data)

    global wish_manager
    storage = LocalStorage(persistence)
    wish_manager = WishManager(storage)

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
