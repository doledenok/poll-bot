from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, ConversationHandler


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

    await context.bot.send_message(update.effective_chat.id, "Please choose the scenario:", reply_markup=reply_markup)
    return CHOOSING_ROLE
