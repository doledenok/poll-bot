import os
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


if __name__ == "__main__":
    if not (token := os.environ.get("TELEGRAM_POLL_BOT_TOKEN")):
        print("Can't find telegram token! Please set TELEGRAM_POLL_BOT_TOKEN environment variable.")
        sys.exit(1)

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler('start', start))

    application.run_polling()
