from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    MessageHandler,
)


USER_STATES_BASE = 100

(
    USER_MAIN,
    USER_NAME,
    USER_INPUT_ID,
    USER_LIST_OF_PARTICIPANTS,
    USER_CHOOSE_RATE,
    USER_RATE_CALMNESS_STORY,
    USER_RATE_CALMNESS_QUESTIONS,
    USER_RATE_EYE_CONTACT_STORY,
    USER_RATE_EYE_CONTACT_QUESTIONS,
    USER_RATE_ANSWERS_SKILL,
    USER_RATE_NOTES,
    USER_FINISH_EXAM,
) = range(USER_STATES_BASE, USER_STATES_BASE + 12)


async def user_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "user_start":
        update.message.reply_text("Please enter your name:")
        await user_name(update, context)
        return USER_NAME
    #elif query.data == "user_name":
    #    await user_set_name(update, context)
    await query.answer("Not implemented yet")


async def user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    print(f"GOT NAME: {name}")


user_states = {
    USER_MAIN: [MessageHandler(filters.ALL, user_main)],
    # TODO
}
