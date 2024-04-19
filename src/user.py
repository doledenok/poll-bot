from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    filters,
    MessageHandler,
)


USER_STATES_BASE = 100

(
    USER_MAIN,
    USER_INPUT_ID,
    USER_NAME,
    USER_LIST_OF_SPEAKERS,
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
    #### TODO: убрать
    context.user_data["exam_id"] = 10
    #################
    if query.data == "user_start":
        await query.answer()
        await context.bot.send_message(update.effective_chat.id, "Please enter exam id. Creator of exam should tell it to you:")
        return USER_INPUT_ID
    await query.answer("How have you done it? Bot is inconsistent.")


async def user_input_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    exam_id = update.message.text
    print(context.user_data)
    if not exam_id.isdigit():
        await update.message.reply_text("Please enter the number:")
        return USER_INPUT_ID

    exam_id = int(exam_id)
    if context.user_data["exam_id"] != exam_id:
        await update.message.reply_text("Please enter the exsisted exam id:")
        return USER_INPUT_ID

    await update.message.reply_text("Success! You are connected to the exam")
    await update.message.reply_text("Please enter your name and surname:")
    return USER_NAME


async def user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    context.user_data["name"] = name
    await update.message.reply_text(f"Hello {name}!")

    #### TODO: убрать
    speakers = ["Max", "Anton", "Gleb", "Ann", "Sergei", "Max", "Anton", "Gleb", "Ann", "Sergei"]
    #################
    keyboard = [[InlineKeyboardButton(f"{speakers[j]}", callback_data=f"user_speaker{j}") for j in range(i, min(len(speakers), i + 3))] for i in range(0, len(speakers), 3)]
    print(keyboard)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Here is the list of speakers. Choose who you want to rate:", reply_markup=reply_markup)
    
    return USER_LIST_OF_SPEAKERS


async def user_list_of_speakers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await context.bot.send_message(update.effective_chat.id, f"You chose {query.data}")
    return USER_INPUT_ID


user_states = {
    USER_MAIN: [MessageHandler(filters.ALL, user_main)],
    USER_INPUT_ID: [MessageHandler(filters.ALL, user_input_id)],
    USER_NAME: [MessageHandler(filters.ALL, user_name)],
    USER_LIST_OF_SPEAKERS: [CallbackQueryHandler(user_list_of_speakers, pattern="^user_speaker*")],
}
