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
    USER_SHOW_LIST_OF_SPEAKERS,
    USER_STORE_SPEAKER_ID,
    USER_SHOW_CRITERIA,
    USER_CHOOSE_RATE,
    USER_RATE_CALMNESS_STORY_STORE,
    USER_RATE_CALMNESS_QUESTIONS_STORE,
    USER_RATE_EYE_CONTACT_STORY_STORE,
    USER_RATE_EYE_CONTACT_QUESTIONS_STORE,
    USER_RATE_ANSWERS_SKILL_STORE,
    USER_RATE_NOTES_STORE,
    USER_FINISH_EXAM,
) = range(USER_STATES_BASE, USER_STATES_BASE + 14)


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
        await update.message.reply_text("Please enter the number - exam id:")
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
    return await user_show_list_of_speakers(update, context)


async def user_show_list_of_speakers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #### TODO: убрать
    speakers = ["Max", "Anton", "Gleb", "Ann", "Sergei", "Max", "Anton", "Gleb", "Ann", "Sergei"]
    #################
    keyboard = [[InlineKeyboardButton(f"{speakers[j]}", callback_data=f"user_speaker{j}") for j in range(i, min(len(speakers), i + 3))] for i in range(0, len(speakers), 3)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(update.effective_chat.id, "Here is the list of speakers. Choose who you want to rate:", reply_markup=reply_markup)
    return USER_STORE_SPEAKER_ID


async def user_store_speaker_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    # TODO: Сохранить в context.user_data id спикера, которого сейчас оцениваем
    await context.bot.send_message(update.effective_chat.id, f"You chose {query.data}")
    return await user_show_criteria(update, context)


async def user_show_criteria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Calmness while telling a story", callback_data=f"user_rate_calmness_story")],
        [InlineKeyboardButton("Calmness while answering questions", callback_data=f"user_rate_calmness_answers")],
        [InlineKeyboardButton("Eye contact while telling a story", callback_data=f"user_rate_eye_contact_story")],
        [InlineKeyboardButton("Eye contact while answering questions", callback_data=f"user_rate_eye_contact_answers")],
        [InlineKeyboardButton("The skill to answer questions", callback_data=f"user_rate_answers_skill")],
        [InlineKeyboardButton("Notes about performance", callback_data=f"user_rate_notes")],
        [InlineKeyboardButton("Choose another speaker", callback_data=f"user_speakers")],
        [InlineKeyboardButton("Finish rating", callback_data=f"user_finish")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(update.effective_chat.id, "Choose what do you want to rate:", reply_markup=reply_markup)
    return USER_CHOOSE_RATE


async def user_rate_calmness_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "Input number from 0 to 10 where 10 is excellent")
    return USER_RATE_CALMNESS_STORY_STORE


async def user_rate_calmness_story_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сохранить оценку
    await context.bot.send_message(update.effective_chat.id, "Thanks! Stored.")
    return await user_show_criteria(update, context)


async def user_rate_calmness_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "Input number from 0 to 10 where 10 is excellent")
    return USER_RATE_CALMNESS_QUESTIONS_STORE


async def user_rate_calmness_questions_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сохранить оценку
    await context.bot.send_message(update.effective_chat.id, "Thanks! Stored.")
    return await user_show_criteria(update, context)


async def user_rate_eye_contact_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "Input number from 0 to 10 where 10 is excellent")
    return USER_RATE_EYE_CONTACT_STORY_STORE


async def user_rate_eye_contact_story_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сохранить оценку
    await context.bot.send_message(update.effective_chat.id, "Thanks! Stored.")
    return await user_show_criteria(update, context)


async def user_rate_eye_contact_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "Input number from 0 to 10 where 10 is excellent")
    return USER_RATE_EYE_CONTACT_QUESTIONS_STORE


async def user_rate_eye_contact_questions_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сохранить оценку
    await context.bot.send_message(update.effective_chat.id, "Thanks! Stored.")
    return await user_show_criteria(update, context)


async def user_rate_answers_skill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "Input number from 0 to 10 where 10 is excellent")
    return USER_RATE_ANSWERS_SKILL_STORE


async def user_rate_answers_skill_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сохранить оценку
    await context.bot.send_message(update.effective_chat.id, "Thanks! Stored.")
    return await user_show_criteria(update, context)


async def user_rate_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "Input number from 0 to 10 where 10 is excellent")
    return USER_RATE_NOTES_STORE


async def user_rate_notes_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сохранить оценку
    await context.bot.send_message(update.effective_chat.id, "Thanks! Stored.")
    return await user_show_criteria(update, context)


async def user_finish_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "Thank you for participating in the exam! Good luck!")
    # TODO: Подумать, как нормально завершать


user_states = {
    USER_MAIN: [MessageHandler(filters.ALL, user_main)],
    USER_INPUT_ID: [MessageHandler(filters.ALL, user_input_id)],
    USER_NAME: [MessageHandler(filters.ALL, user_name)],
    USER_SHOW_LIST_OF_SPEAKERS: [MessageHandler(filters.ALL, user_show_list_of_speakers)],
    USER_STORE_SPEAKER_ID: [CallbackQueryHandler(user_store_speaker_id, pattern="^user_speaker*")],
    USER_SHOW_CRITERIA: [MessageHandler(filters.ALL, user_show_criteria)],
    USER_CHOOSE_RATE: [
        CallbackQueryHandler(user_rate_calmness_story, pattern="^user_rate_calmness_story$"),
        CallbackQueryHandler(user_rate_calmness_questions, pattern="^user_rate_calmness_questions$"),
        CallbackQueryHandler(user_rate_eye_contact_story, pattern="^user_rate_eye_contact_story$"),
        CallbackQueryHandler(user_rate_eye_contact_questions, pattern="^user_rate_eye_contact_questions$"),
        CallbackQueryHandler(user_rate_answers_skill, pattern="^user_rate_answers_skill$"),
        CallbackQueryHandler(user_rate_notes, pattern="^user_rate_notes$"),
        CallbackQueryHandler(user_show_list_of_speakers, pattern="^user_speakers$"),
    ],
    USER_RATE_CALMNESS_STORY_STORE: [MessageHandler(filters.ALL, user_rate_calmness_story_store)],
    USER_RATE_CALMNESS_QUESTIONS_STORE: [MessageHandler(filters.ALL, user_rate_calmness_questions_store)],
    USER_RATE_EYE_CONTACT_STORY_STORE: [MessageHandler(filters.ALL, user_rate_eye_contact_story_store)],
    USER_RATE_EYE_CONTACT_QUESTIONS_STORE: [MessageHandler(filters.ALL, user_rate_eye_contact_questions_store)],
    USER_RATE_ANSWERS_SKILL_STORE: [MessageHandler(filters.ALL, user_rate_answers_skill_store)],
    USER_RATE_NOTES_STORE: [MessageHandler(filters.ALL, user_rate_notes_store)],
    USER_FINISH_EXAM: [MessageHandler(filters.ALL, user_finish_exam)],
}
