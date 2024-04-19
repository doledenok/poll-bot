import os
import sys
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, ConversationHandler
from admin import admin_main, admin_states
from user import user_main, user_states


# First state after start
CHOOSING_ROLE = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Output the start menu with role choice - admin or user.
    """
    keyboard = [
        [
            InlineKeyboardButton("Create exam", callback_data="admin_start"),
            InlineKeyboardButton("Join exam", callback_data="user_start"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose the scenario:", reply_markup=reply_markup)
    return CHOOSING_ROLE


def main():
    if not (token := os.environ.get("TELEGRAM_POLL_BOT_TOKEN")):
        print("Can't find telegram token! Please set TELEGRAM_POLL_BOT_TOKEN environment variable.")
        sys.exit(1)

    application = ApplicationBuilder().token(token).build()

    states = {
            CHOOSING_ROLE: [
                CallbackQueryHandler(admin_main, pattern="^admin_start"),
                CallbackQueryHandler(user_main, pattern="^user_start"),
            ],
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
