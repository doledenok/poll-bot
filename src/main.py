import os
import sys
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, ConversationHandler

from start import start, choosing_language, CHOOSING_ROLE, CHOOSING_LANGUAGE
from admin import admin_main, admin_states
from user import user_main, user_states


def main():
    if not (token := os.environ.get("TELEGRAM_POLL_BOT_TOKEN")):
        print("Can't find telegram token! Please set TELEGRAM_POLL_BOT_TOKEN environment variable.")
        sys.exit(1)

    application = ApplicationBuilder().token(token).build()

    states = {
            CHOOSING_LANGUAGE: [
                CallbackQueryHandler(choosing_language, pattern="^interface_language"),
            ],
            CHOOSING_ROLE: [
                CallbackQueryHandler(admin_main, pattern="^admin_start"),
                CallbackQueryHandler(user_main, pattern="^user_start"),
            ]
        }
    states |= admin_states | user_states

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states=states,
        fallbacks=[CommandHandler("start", start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
