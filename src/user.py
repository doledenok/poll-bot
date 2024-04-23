"""User role realization."""

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    filters,
    MessageHandler,
)

from exam import Exam, ExamStatus
from start import start
import messages


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
    """
    First function of user role.

    It is called after user choose the joining exam scenario.
    """
    query = update.callback_query

    if query.data == "user_start":
        await query.answer()
        user_language = context.user_data["user_language"]
        # TODO: убрать
        if "exams" not in context.bot_data:
            context.bot_data["exams"] = {}
        context.bot_data["exams"][42] = Exam(42)
        context.bot_data["exams"][42].add_speaker("Max Doledenok")
        context.bot_data["exams"][42].add_speaker("Kirill Nikorov")
        #################
        await context.bot.send_message(update.effective_chat.id, messages.EXAM_ID_ENTERING[user_language])
        return USER_INPUT_ID
    await query.answer(messages.INCONSISTENCY_MESSAGE[user_language])


async def user_input_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process user entered exam id to join existed exam."""
    user_language = context.user_data["user_language"]
    exam_id = update.message.text
    if not exam_id.isdigit():
        await update.message.reply_text(messages.EXAM_ID_ENTERING_NOT_NUMBER_ERROR[user_language])
        return USER_INPUT_ID

    exam_id = int(exam_id)
    if "exams" not in context.bot_data or exam_id not in context.bot_data["exams"]:
        if "exams" not in context.bot_data:
            await update.message.reply_text(messages.EXAM_ID_ENTERING_NO_EXAMS_ERROR[user_language])
            return USER_INPUT_ID
        elif exam_id not in context.bot_data["exams"]:
            await update.message.reply_text(messages.EXAM_ID_ENTERING_NOT_REGISTRATED_ERROR[user_language] % exam_id)
        return USER_INPUT_ID
    context.user_data["exam_id"] = exam_id
    context.user_data["exam"] = context.bot_data["exams"][exam_id]
    await update.message.reply_text(messages.EXAM_ID_ENTERING_SUCCESS[user_language])
    await update.message.reply_text(messages.NAME_ENTERING[user_language])
    return USER_NAME


async def user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add user name to the list of speakers. And invite user to start listening."""
    user_language = context.user_data["user_language"]
    name = update.message.text
    context.user_data["name"] = name
    user_id = context.user_data["exam"].add_speaker(name)
    if user_id is None:
        context.bot.send_message(update.effective_chat.id, messages.NAME_ENTERING_COLLISION_ERROR[user_language])
        return USER_NAME
    context.user_data["user_id"] = user_id
    keyboard = [[InlineKeyboardButton(messages.START_LISTENING[user_language], callback_data="user_start_listening")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(messages.GREETING_MESSAGE[user_language] % name, reply_markup=reply_markup)
    return USER_SHOW_LIST_OF_SPEAKERS


async def user_show_list_of_speakers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """If exam is started - then print speakers list and invite user to rate them."""
    query = update.callback_query
    await query.answer()
    user_language = context.user_data["user_language"]

    while context.user_data["exam"].exam_status != ExamStatus.RegistrationFinished:
        keyboard = [
            [InlineKeyboardButton(messages.START_LISTENING[user_language], callback_data="user_start_listening")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            update.effective_chat.id,
            text=messages.EXAM_REGISTRATION_NOT_FINISHED[user_language],
            reply_markup=reply_markup,
        )
        return USER_SHOW_LIST_OF_SPEAKERS

    speakers = context.user_data["exam"].get_speaker_names(context.user_data["user_id"])
    keyboard = [
        [
            InlineKeyboardButton(f"{speakers[j]}", callback_data=f"user_speaker{j}")
            for j in range(i, min(len(speakers), i + 3))
        ]
        for i in range(0, len(speakers), 3)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        update.effective_chat.id, messages.SPEAKERS_LIST_TO_RATE[user_language], reply_markup=reply_markup
    )
    return USER_STORE_SPEAKER_ID


async def user_store_speaker_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store speaker that user want to rate now and show the criteria of rating."""
    query = update.callback_query
    await query.answer()
    user_language = context.user_data["user_language"]

    if query.data.startswith("user_speaker"):
        speaker_id = int(query.data[len("user_speaker"):])
        context.user_data["speaker_id"] = speaker_id
    else:
        await query.answer(messages.INCONSISTENCY_MESSAGE[user_language])
        return

    await context.bot.send_message(
        update.effective_chat.id,
        messages.SPEAKER_TO_RATE_CHOICE[user_language] % context.user_data['exam'].get_name_by_id(speaker_id),
    )
    return await user_show_criteria(update, context)


async def user_show_criteria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the criteria of rating."""
    user_language = context.user_data["user_language"]
    keyboard = [
        [InlineKeyboardButton(messages.CALMNESS_STORY[user_language], callback_data="user_rate_calmness_story")],
        [
            InlineKeyboardButton(
                messages.CALMNESS_QUESTIONS[user_language], callback_data="user_rate_calmness_questions"
            )
        ],
        [InlineKeyboardButton(messages.EYE_STORY[user_language], callback_data="user_rate_eye_contact_story")],
        [InlineKeyboardButton(messages.EYE_QUESTIONS[user_language], callback_data="user_rate_eye_contact_questions")],
        [InlineKeyboardButton(messages.ANSWER_SKILL[user_language], callback_data="user_rate_answers_skill")],
        [InlineKeyboardButton(messages.NOTES_OF_LISTENER[user_language], callback_data="user_rate_notes")],
        [InlineKeyboardButton(messages.CHOOSE_ANOTHER_SPEAKER[user_language], callback_data="user_speakers")],
        [InlineKeyboardButton(messages.FINISH_RATING[user_language], callback_data="user_finish_exam")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        update.effective_chat.id, messages.CHOOSE_FIELD_TO_RATE[user_language], reply_markup=reply_markup
    )
    return USER_CHOOSE_RATE


async def user_get_one_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Support function for getting number between 0 and 10."""
    user_language = context.user_data["user_language"]
    answer = update.message.text
    if not answer.isdigit():
        await context.bot.send_message(update.effective_chat.id, messages.RATE_ENTERING_NOT_NUMBER_ERROR[user_language])
        return None
    score = int(answer)
    if not 0 <= score <= 10:
        await context.bot.send_message(update.effective_chat.id, messages.RATE_ENTERING_RANGE_ERROR[user_language])
        return None
    return score


async def user_rate_calmness_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rate calmness while telling the story."""
    user_language = context.user_data["user_language"]
    await context.bot.send_message(update.effective_chat.id, messages.RATE_ENTERING_DESCRIPTION[user_language])
    return USER_RATE_CALMNESS_STORY_STORE


async def user_rate_calmness_story_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store the score of calmness while telling the story."""
    user_language = context.user_data["user_language"]
    score = await user_get_one_number(update, context)
    if score is None:
        return await user_show_criteria(update, context)
    context.user_data["exam"].add_answer(
        context.user_data["user_id"], context.user_data["speaker_id"], "calmness_story", score
    )
    await context.bot.send_message(update.effective_chat.id, messages.RATE_ENTERING_THANKS[user_language])
    return await user_show_criteria(update, context)


async def user_rate_calmness_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rate calmness while answering the questions."""
    user_language = context.user_data["user_language"]
    await context.bot.send_message(update.effective_chat.id, messages.RATE_ENTERING_DESCRIPTION[user_language])
    return USER_RATE_CALMNESS_QUESTIONS_STORE


async def user_rate_calmness_questions_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store the score of calmness while answering the questions."""
    user_language = context.user_data["user_language"]
    score = await user_get_one_number(update, context)
    if score is None:
        return await user_show_criteria(update, context)
    context.user_data["exam"].add_answer(
        context.user_data["user_id"], context.user_data["speaker_id"], "calmness_questions", score
    )
    await context.bot.send_message(update.effective_chat.id, messages.RATE_ENTERING_THANKS[user_language])
    return await user_show_criteria(update, context)


async def user_rate_eye_contact_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rate eye contact while telling the story."""
    user_language = context.user_data["user_language"]
    await context.bot.send_message(update.effective_chat.id, messages.RATE_ENTERING_DESCRIPTION[user_language])
    return USER_RATE_EYE_CONTACT_STORY_STORE


async def user_rate_eye_contact_story_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store the score of eye contact while telling the story."""
    user_language = context.user_data["user_language"]
    score = await user_get_one_number(update, context)
    if score is None:
        return await user_show_criteria(update, context)
    context.user_data["exam"].add_answer(
        context.user_data["user_id"], context.user_data["speaker_id"], "eye_contact_story", score
    )
    await context.bot.send_message(update.effective_chat.id, messages.RATE_ENTERING_THANKS[user_language])
    return await user_show_criteria(update, context)


async def user_rate_eye_contact_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rate eye contact while answering the questions."""
    user_language = context.user_data["user_language"]
    await context.bot.send_message(update.effective_chat.id, messages.RATE_ENTERING_DESCRIPTION[user_language])
    return USER_RATE_EYE_CONTACT_QUESTIONS_STORE


async def user_rate_eye_contact_questions_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store the score of eye contact while answering the questions."""
    user_language = context.user_data["user_language"]
    score = await user_get_one_number(update, context)
    if score is None:
        return await user_show_criteria(update, context)
    context.user_data["exam"].add_answer(
        context.user_data["user_id"], context.user_data["speaker_id"], "eye_contact_quesitons", score
    )
    await context.bot.send_message(update.effective_chat.id, messages.RATE_ENTERING_THANKS[user_language])
    return await user_show_criteria(update, context)


async def user_rate_answers_skill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rate skill of answering questions."""
    user_language = context.user_data["user_language"]
    await context.bot.send_message(update.effective_chat.id, messages.RATE_ENTERING_DESCRIPTION[user_language])
    return USER_RATE_ANSWERS_SKILL_STORE


async def user_rate_answers_skill_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store the score of skill of answering questions."""
    user_language = context.user_data["user_language"]
    score = await user_get_one_number(update, context)
    if score is None:
        return await user_show_criteria(update, context)
    context.user_data["exam"].add_answer(
        context.user_data["user_id"], context.user_data["speaker_id"], "answer_skill", score
    )
    await context.bot.send_message(update.effective_chat.id, messages.RATE_ENTERING_THANKS[user_language])
    return await user_show_criteria(update, context)


async def user_rate_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add some notes about speaker performance."""
    user_language = context.user_data["user_language"]
    await context.bot.send_message(update.effective_chat.id, messages.NOTES_OF_LISTENER_ENTERING[user_language])
    return USER_RATE_NOTES_STORE


async def user_rate_notes_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store some notes about speaker performance."""
    user_language = context.user_data["user_language"]
    context.user_data["exam"].add_answer(
        context.user_data["user_id"], context.user_data["speaker_id"], "notes", update.message.text
    )
    await context.bot.send_message(update.effective_chat.id, messages.RATE_ENTERING_THANKS[user_language])
    return await user_show_criteria(update, context)


async def user_finish_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finish exam and print the start menu."""
    user_language = context.user_data["user_language"]
    await context.bot.send_message(update.effective_chat.id, messages.RATE_PARTICIPATION_THANKS[user_language])
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
