from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    filters,
    MessageHandler,
)
from exam import Exam, ExamStatus
from start import start
import time


"""
В context.bot_data["exams"] находятся объекты класса exam.Exam, где хранится вся информация об экзаменах
В context.user_data есть ключи:
 - exam_id - id экзамена для текущего пользователя
 - exam - объект класса exam.Exam
 - name - имя пользователя
 - user_id - id пользователя
 - speaker_id - id выступающего, которого сейчас оценивает пользователь
"""


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
) = range(USER_STATES_BASE, USER_STATES_BASE + 13)


async def user_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == "user_start":
        await query.answer()
        #### TODO: убрать
        if "exams" not in context.bot_data:
            context.bot_data["exams"] = {}
        context.bot_data["exams"][42] = Exam(42)
        context.bot_data["exams"][42].add_speaker("Max Doledenok")
        context.bot_data["exams"][42].add_speaker("Kirill Nikorov")
        #################
        await context.bot.send_message(update.effective_chat.id, "Please enter exam id. Creator of exam should tell it to you:")
        return USER_INPUT_ID
    await query.answer("How have you done it? Bot is inconsistent.")


async def user_input_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    exam_id = update.message.text
    if not exam_id.isdigit():
        await update.message.reply_text("Please enter the number - exam id:")
        return USER_INPUT_ID

    exam_id = int(exam_id)
    if "exams" not in context.bot_data or exam_id not in context.bot_data["exams"]:
        if "exams" not in context.bot_data:
            await update.message.reply_text("The is no registrated exams. Wait for exam creation")
            return USER_INPUT_ID
        elif exam_id not in context.bot_data["exams"]:
            await update.message.reply_text(f"Exam {exam_id} is not registered. Please enter the existed exam id:")
        return USER_INPUT_ID
    context.user_data["exam_id"] = exam_id
    context.user_data["exam"] = context.bot_data["exams"][exam_id]
    await update.message.reply_text("Success! You are connected to the exam")
    await update.message.reply_text("Please enter your name and surname:")
    return USER_NAME


async def user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    context.user_data["name"] = name
    user_id = context.user_data["exam"].add_speaker(name)
    if user_id is None:
        context.bot.send_message(update.effective_chat.id, "This name already exists! Enter another please")
        return USER_NAME
    context.user_data["user_id"] = user_id
    keyboard = [[InlineKeyboardButton("Start listening", callback_data="user_start_listening")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Hello {name}!\nLet's wait till exam creator finishes the registration and start our speakers listening.",
                                    reply_markup=reply_markup)
    return USER_SHOW_LIST_OF_SPEAKERS


async def user_show_list_of_speakers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    while context.user_data["exam"].exam_status != ExamStatus.RegistrationFinished:
        keyboard = [[InlineKeyboardButton("Start listening", callback_data="user_start_listening")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(update.effective_chat.id,
                                       text=f"Sorry, exam creator has not finished exam registration yet. Check it again a bit later.",
                                       reply_markup=reply_markup)
        return USER_SHOW_LIST_OF_SPEAKERS

    speakers = context.user_data["exam"].get_speaker_names(context.user_data["user_id"])
    keyboard = [[InlineKeyboardButton(f"{speakers[j]}", callback_data=f"user_speaker{j}") for j in range(i, min(len(speakers), i + 3))] for i in range(0, len(speakers), 3)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(update.effective_chat.id, "Here is the list of speakers. Choose who you want to rate:", reply_markup=reply_markup)
    return USER_STORE_SPEAKER_ID


async def user_store_speaker_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("user_speaker"):
        speaker_id = int(query.data[len("user_speaker"):])
        context.user_data["speaker_id"] = speaker_id
    else:
        await query.answer("How have you done it? Bot is inconsistent.")
        return

    await context.bot.send_message(update.effective_chat.id, f"You chose {context.user_data['exam'].get_name_by_id(speaker_id)}")
    return await user_show_criteria(update, context)


async def user_show_criteria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Calmness while telling a story", callback_data=f"user_rate_calmness_story")],
        [InlineKeyboardButton("Calmness while answering questions", callback_data=f"user_rate_calmness_questions")],
        [InlineKeyboardButton("Eye contact while telling a story", callback_data=f"user_rate_eye_contact_story")],
        [InlineKeyboardButton("Eye contact while answering questions", callback_data=f"user_rate_eye_contact_questions")],
        [InlineKeyboardButton("The skill to answer questions", callback_data=f"user_rate_answers_skill")],
        [InlineKeyboardButton("Notes about performance", callback_data=f"user_rate_notes")],
        [InlineKeyboardButton("Choose another speaker", callback_data=f"user_speakers")],
        [InlineKeyboardButton("Finish rating", callback_data=f"user_finish_exam")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(update.effective_chat.id, "Choose what do you want to rate:", reply_markup=reply_markup)
    return USER_CHOOSE_RATE


async def user_get_one_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Support function for getting number between 0 and 10.
    """
    answer = update.message.text
    if not answer.isdigit():
        await context.bot.send_message(update.effective_chat.id, "Please enter the number!")
        return None
    score = int(answer)
    if not 0 <= score <= 10:
        await context.bot.send_message(update.effective_chat.id, "Please enter the number between 0 and 10!")
        return None
    return score


async def user_rate_calmness_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "Input number from 0 to 10 where 10 is excellent")
    return USER_RATE_CALMNESS_STORY_STORE


async def user_rate_calmness_story_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = await user_get_one_number(update, context)
    if score == None:
        return await user_show_criteria(update, context)
    context.user_data["exam"].add_answer(
        context.user_data["user_id"],
        context.user_data["speaker_id"],
        "calmness_story",
        score)
    await context.bot.send_message(update.effective_chat.id, "Thanks! Stored.")
    return await user_show_criteria(update, context)


async def user_rate_calmness_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "Input number from 0 to 10 where 10 is excellent")
    return USER_RATE_CALMNESS_QUESTIONS_STORE


async def user_rate_calmness_questions_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = await user_get_one_number(update, context)
    if score == None:
        return await user_show_criteria(update, context)
    context.user_data["exam"].add_answer(
        context.user_data["user_id"],
        context.user_data["speaker_id"],
        "calmness_questions",
        score)
    await context.bot.send_message(update.effective_chat.id, "Thanks! Stored.")
    return await user_show_criteria(update, context)


async def user_rate_eye_contact_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "Input number from 0 to 10 where 10 is excellent")
    return USER_RATE_EYE_CONTACT_STORY_STORE


async def user_rate_eye_contact_story_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = await user_get_one_number(update, context)
    if score == None:
        return await user_show_criteria(update, context)
    context.user_data["exam"].add_answer(
        context.user_data["user_id"],
        context.user_data["speaker_id"],
        "eye_contact_story",
        score)
    await context.bot.send_message(update.effective_chat.id, "Thanks! Stored.")
    return await user_show_criteria(update, context)


async def user_rate_eye_contact_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "Input number from 0 to 10 where 10 is excellent")
    return USER_RATE_EYE_CONTACT_QUESTIONS_STORE


async def user_rate_eye_contact_questions_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = await user_get_one_number(update, context)
    if score == None:
        return await user_show_criteria(update, context)
    context.user_data["exam"].add_answer(
        context.user_data["user_id"],
        context.user_data["speaker_id"],
        "eye_contact_quesitons",
        score)
    await context.bot.send_message(update.effective_chat.id, "Thanks! Stored.")
    return await user_show_criteria(update, context)


async def user_rate_answers_skill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "Input number from 0 to 10 where 10 is excellent")
    return USER_RATE_ANSWERS_SKILL_STORE


async def user_rate_answers_skill_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = await user_get_one_number(update, context)
    if score == None:
        return await user_show_criteria(update, context)
    context.user_data["exam"].add_answer(
        context.user_data["user_id"],
        context.user_data["speaker_id"],
        "answer_skill",
        score)
    await context.bot.send_message(update.effective_chat.id, "Thanks! Stored.")
    return await user_show_criteria(update, context)


async def user_rate_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "Enter notes you want to save:")
    return USER_RATE_NOTES_STORE


async def user_rate_notes_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["exam"].add_answer(
        context.user_data["user_id"],
        context.user_data["speaker_id"],
        "notes",
        update.message.text)
    await context.bot.send_message(update.effective_chat.id, "Thanks! Stored.")
    return await user_show_criteria(update, context)


async def user_finish_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "Thank you for participating in the exam!\nNow you can wait for exam finish to see the global and individual results.\nGood luck!")
    return await start(update, context)


user_states = {
    USER_MAIN: [MessageHandler(filters.ALL, user_main)],
    USER_INPUT_ID: [MessageHandler(filters.ALL, user_input_id)],
    USER_NAME: [MessageHandler(filters.ALL, user_name)],
    USER_SHOW_LIST_OF_SPEAKERS: [CallbackQueryHandler(user_show_list_of_speakers, pattern="^user_start_listening$")],
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
        CallbackQueryHandler(user_finish_exam, pattern="^user_finish_exam$"),
    ],
    USER_RATE_CALMNESS_STORY_STORE: [MessageHandler(filters.ALL, user_rate_calmness_story_store)],
    USER_RATE_CALMNESS_QUESTIONS_STORE: [MessageHandler(filters.ALL, user_rate_calmness_questions_store)],
    USER_RATE_EYE_CONTACT_STORY_STORE: [MessageHandler(filters.ALL, user_rate_eye_contact_story_store)],
    USER_RATE_EYE_CONTACT_QUESTIONS_STORE: [MessageHandler(filters.ALL, user_rate_eye_contact_questions_store)],
    USER_RATE_ANSWERS_SKILL_STORE: [MessageHandler(filters.ALL, user_rate_answers_skill_store)],
    USER_RATE_NOTES_STORE: [MessageHandler(filters.ALL, user_rate_notes_store)],
}
