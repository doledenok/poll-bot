import os
import sys
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from admin import admin_main
from user import user_main


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Output the start menu with role choice - admin or user.
    """
    keyboard = [
        [
            InlineKeyboardButton("Admin", callback_data="admin"),
            InlineKeyboardButton("User", callback_data="user"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose your role:", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Parses the callback data from pressing some buttons.
    """
    query = update.callback_query

    if query.data == "admin":
        await admin_main(update, context)
    elif query.data == "user":
        await user_main(update, context)
    else:
        # CallbackQueries need to be answered, even if no notification to the user is needed
        await query.answer()


if __name__ == "__main__":
    if not (token := os.environ.get("TELEGRAM_POLL_BOT_TOKEN")):
        print("Can't find telegram token! Please set TELEGRAM_POLL_BOT_TOKEN environment variable.")
        sys.exit(1)

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()
