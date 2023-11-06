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

)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger("wishlist_logger")
log.setLevel(logging.DEBUG)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.debug("'Start' command handler: "
              f"userid = '{update.effective_user.id}', "
              f"username = '{update.effective_user.username}'")

    if context.user_data.get('user_id') is None:
        context.user_data['user_id'] = update.effective_user.id
        context.user_data['user_name'] = update.effective_user.username
        log.debug(f"New user: userid = '{update.effective_user.id}', ")

    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="> " + update.message.text)


def main() -> None:
    parser = argparse.ArgumentParser("WishList telegram bot")
    parser.add_argument('-t', '--token', required=True)
    parser.add_argument('-s', '--storage_path', required=True)
    args = parser.parse_args()

    persistence = PicklePersistence(args.storage_path)
    application = Application.builder().token(args.token).persistence(persistence).build()

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(start_handler)
    application.add_handler(message_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
