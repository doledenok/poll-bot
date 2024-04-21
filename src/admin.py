import os
import sys
import random
import datetime
import csv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, ConversationHandler
from exam import Exam, ExamStatus
from user import user_main, user_states


"""
В context.bot_data["exams"] находятся объекты класса exam.Exam, где хранится вся информация об экзаменах
В context.user_data есть ключи:
 - exam_id - id экзамена для текущего админа
"""


ADMIN_STATES_BASE = 10
AWAITING_FOR_EXAM_REGISTRATION_FINISH = ADMIN_STATES_BASE + 0
ADMIN_FINISH_EXAM_COMMAND = ADMIN_STATES_BASE + 1
ADMIN_CHOOSING_STUDENT_FOR_EXAM_RESULTS_REVIEW = ADMIN_STATES_BASE + 2
ADMIN_FINISH_EXAM_RESULTS_REVIEW = ADMIN_STATES_BASE + 3


async def admin_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    if query.data == "admin_start":
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"So your scenario is {query.data.replace('_', ' ')}")
    else:
        print(f'Strange query data {query.data} in admin_main', file=sys.stderr)
        return

    #### TODO: раскомментить
    generated_exam_id = int(1)  # int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))  # TODO: идеально случайно сгенерированный id
    #################
    if "exams" not in context.bot_data:
        context.bot_data["exams"] = {}
    context.bot_data["exams"][generated_exam_id] = Exam(generated_exam_id)
    context.user_data["exam_id"] = generated_exam_id
    context.user_data["exam"] = context.bot_data["exams"][generated_exam_id]
    #### TODO: убрать
    context.bot_data["exams"][generated_exam_id].add_speaker("Max Doledenok")
    context.bot_data["exams"][generated_exam_id].add_speaker("Kirill Nikorov")
    #################

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your exam id is {generated_exam_id}")

    return await admin_print_exam_registration_finish(update, context)


async def admin_print_exam_registration_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Finish registration and show students list", callback_data="admin_student_list"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Open students list when you are ready to finish registration and to start exam:", reply_markup=reply_markup)
    return AWAITING_FOR_EXAM_REGISTRATION_FINISH

async def admin_exam_registration_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data != "admin_student_list":
        print(f'Strange query data {query.data} in admin_student_list', file=sys.stderr)
        return
    context.user_data["exam"].exam_status = ExamStatus.RegistrationFinished
    student_list_for_exam = context.bot_data["exams"][context.user_data["exam_id"]].get_speaker_names()
    if not student_list_for_exam:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No registered student! Please try later.")
        return await admin_print_exam_registration_finish(update, context)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=", ".join(student_list_for_exam))

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Now you can listen to your students. When all your students finish their presentations, please, send command /finish_exam")
    return ADMIN_FINISH_EXAM_COMMAND

async def admin_finish_exam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Output the start menu with role choice - admin or user.
    """
    context.user_data["exam"].exam_status = ExamStatus.PresentationsFinished
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Your exam is finished. Now we start to aggregate all results")

    saved_rows = context.user_data["exam"].save_results('/home/knikorov/Studing/PythonDevelopment2024/poll-bot/data/exams_db.csv')
    print(f'Processed and saved {saved_rows} rows for exam {context.user_data["exam_id"]}')

    # Видимо, это лучше сделать через KeyboardMarkup, чтобы не спамить каждый раз таблицей-сообщением
    student_list_for_exam = context.bot_data["exams"][context.user_data["exam_id"]].get_speaker_names()
    number_of_students_on_exam = len(student_list_for_exam)
    N_COLS = 3
    N_ROWS = number_of_students_on_exam // N_COLS + int(number_of_students_on_exam % N_COLS != 0)
    students_results = [[f'{student_list_for_exam[i*N_COLS + j]}' if (i*N_COLS + j < number_of_students_on_exam)
                                                                  else '' for j in range(N_COLS)] for i in range(N_ROWS)]

    keyboard = []
    for i in range(N_ROWS):
        current_row = []
        for j in range(N_COLS):
            current_row.append(InlineKeyboardButton(students_results[i][j], callback_data=f"admin_student_{i*N_COLS + j}_results"))
        keyboard.append(current_row)
    keyboard.append([InlineKeyboardButton("Finish results review", callback_data=f"admin_finish_review_results")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Your per-student exam results are here:", reply_markup=reply_markup)

    return ADMIN_CHOOSING_STUDENT_FOR_EXAM_RESULTS_REVIEW

async def admin_choosing_student_for_exam_results_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.endswith("_results"):
        print(f'Strange query data {query.data} in admin_exam_registration_finish', file=sys.stderr)
        return

    if query.data == 'admin_finish_review_results':
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You've clicked finish-button.\nCongratulations! A lot of your students are doing better!")
        return ADMIN_FINISH_EXAM_RESULTS_REVIEW

    results = ["perfect", "good", "bad"]
    student_name = ' '.join(query.data.split('_')[1: -1]).capitalize()
    student_result = random.choice(results)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{student_name} results are {student_result}")

    # Видимо, это лучше сделать через KeyboardMarkup, чтобы не спамить каждый раз таблицей-сообщением
    student_list_for_exam = context.bot_data["exams"][context.user_data["exam_id"]].get_speaker_names()
    number_of_students_on_exam = len(student_list_for_exam)
    N_COLS = 3
    N_ROWS = number_of_students_on_exam // N_COLS + int(number_of_students_on_exam % N_COLS != 0)
    students_results = [[f'{student_list_for_exam[i*N_COLS + j]}' if (i*N_COLS + j < number_of_students_on_exam)
                                                                  else '' for j in range(N_COLS)] for i in range(N_ROWS)]

    keyboard = []
    for i in range(N_ROWS):
        current_row = []
        for j in range(N_COLS):
            current_row.append(InlineKeyboardButton(students_results[i][j], callback_data=f"admin_student_{i*N_COLS + j}_results"))
        keyboard.append(current_row)
    keyboard.append([InlineKeyboardButton("Finish results review", callback_data=f"admin_finish_review_results")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Your per-student exam results are here:", reply_markup=reply_markup)

    return ADMIN_CHOOSING_STUDENT_FOR_EXAM_RESULTS_REVIEW


admin_states = {
    AWAITING_FOR_EXAM_REGISTRATION_FINISH: [
        CallbackQueryHandler(admin_exam_registration_finish, pattern="^admin*"),
    ],
    ADMIN_FINISH_EXAM_COMMAND: [
        CommandHandler("finish_exam", admin_finish_exam_command)
    ],
    ADMIN_CHOOSING_STUDENT_FOR_EXAM_RESULTS_REVIEW: [
        CallbackQueryHandler(admin_choosing_student_for_exam_results_button, pattern="^admin*"),
    ]
}
