import os
import sys
import random
import datetime
import csv
import telegram
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, ConversationHandler
from exam import Exam, ExamStatus
from user import user_main, user_states
import statistics

import messages

EXAMS_DATABASE_PATH = '/home/knikorov/Studing/PythonDevelopment2024/poll-bot/data/exams_db.csv'
STATISTICS_DATABASE_PATH = '/home/knikorov/Studing/PythonDevelopment2024/poll-bot/data/exams_stats_db.csv'

ADMIN_STATES_BASE = 10
AWAITING_FOR_EXAM_REGISTRATION_FINISH = ADMIN_STATES_BASE + 0
ADMIN_FINISH_EXAM_COMMAND = ADMIN_STATES_BASE + 1
ADMIN_CHOOSING_STUDENT_FOR_EXAM_RESULTS_REVIEW = ADMIN_STATES_BASE + 2
ADMIN_FINISH_EXAM_RESULTS_REVIEW = ADMIN_STATES_BASE + 3


async def admin_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_language = context.user_data["user_language"]
    if query.data == "admin_start":
        await context.bot.send_message(chat_id=update.effective_chat.id, text=messages.ADMIN_SCENARIO_INFORM[user_language])
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

    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages.EXAM_ID_CREATION[user_language] % generated_exam_id)

    return await admin_print_exam_registration_finish(update, context)


async def admin_print_exam_registration_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = context.user_data["user_language"]
    keyboard = [
        [
            InlineKeyboardButton(messages.EXAM_REGISTRATION_FINISH_PLUS_STUDENTS_LIST[user_language], callback_data="admin_student_list"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages.EXAM_REGISTRATION_FINISHING_DESCRIPTION[user_language], reply_markup=reply_markup)
    return AWAITING_FOR_EXAM_REGISTRATION_FINISH

async def admin_exam_registration_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_language = context.user_data["user_language"]

    if query.data != "admin_student_list":
        print(f'Strange query data {query.data} in admin_student_list', file=sys.stderr)
        return
    context.user_data["exam"].exam_status = ExamStatus.RegistrationFinished
    student_list_for_exam = context.bot_data["exams"][context.user_data["exam_id"]].get_speaker_names()
    if not student_list_for_exam:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=messages.EXAM_REGISTRATION_FINISHING_NO_STUDENTS_ERROR[user_language])
        return await admin_print_exam_registration_finish(update, context)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=", ".join(student_list_for_exam))

    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages.EXAM_STARTING_PLUS_EXAM_FINISH_COMMAND[user_language])
    return ADMIN_FINISH_EXAM_COMMAND

async def admin_finish_exam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Output the start menu with role choice - admin or user.
    """
    user_language = context.user_data["user_language"]

    context.user_data["exam"].exam_status = ExamStatus.PresentationsFinished
    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages.EXAM_FINISH_PLUS_RESULTS_AGGREGATION[user_language])

    saved_rows = context.user_data["exam"].save_results(EXAMS_DATABASE_PATH)
    print(f'Processed and saved {saved_rows} rows for exam {context.user_data["exam_id"]}', file=sys.stdout)

    statistics.calculate_exam_stats(context.user_data["exam_id"], EXAMS_DATABASE_PATH, STATISTICS_DATABASE_PATH)

    # Видимо, это лучше сделать через KeyboardMarkup, чтобы не спамить каждый раз таблицей-сообщением
    student_list_for_exam = context.user_data["exam"].get_speaker_names()
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
    keyboard.append([InlineKeyboardButton(messages.EXAM_ALL_RESULTS[user_language], callback_data=f"admin_all_students_results")])
    keyboard.append([InlineKeyboardButton(messages.EXAM_FINISH_REVIEW[user_language], callback_data=f"admin_finish_review_results")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages.EXAM_PER_STUDENT_RESULTS[user_language], reply_markup=reply_markup)

    return ADMIN_CHOOSING_STUDENT_FOR_EXAM_RESULTS_REVIEW

async def admin_choosing_student_for_exam_results_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_language = context.user_data["user_language"]

    if not query.data.endswith("_results"):
        print(f'Strange query data {query.data} in admin_exam_registration_finish', file=sys.stderr)
        return

    if query.data == 'admin_finish_review_results':
        await context.bot.send_message(chat_id=update.effective_chat.id, text=messages.EXAM_FINISH_REVIEW_DESCRIPTION[user_language])
        return ADMIN_FINISH_EXAM_RESULTS_REVIEW

    exam_id = context.user_data["exam_id"]
    students_names = context.user_data["exam"].get_speaker_names()
    if query.data == 'admin_all_students_results':
        exam_results = statistics.get_exam_results(exam_id, students_names, STATISTICS_DATABASE_PATH)
        for student_id, student_result in exam_results.items():
            student_name = students_names[student_id]
            # await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*{student_name}* results are\n```{student_result}```\n\n",
            #                                parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=f'{STATISTICS_DATABASE_PATH}_{exam_id}_{student_id}_results.png',
                                        caption=messages.EXAM_INDIVIDUAL_RESULTS[user_language] % (student_name, student_result),
                                        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
    elif query.data.startswith("admin_student_"):
        student_id = int(query.data.split('_')[2])
        student_name = students_names[student_id]
        student_result = statistics.get_student_results(exam_id, student_id, students_names, STATISTICS_DATABASE_PATH)
        # results = ["perfect", "good", "bad"]
        # student_result = random.choice(results)
        # await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*{student_name}* results are\n```{student_result}```",
        #                                parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=f'{STATISTICS_DATABASE_PATH}_{exam_id}_{student_id}_results.png',
                                       caption=messages.EXAM_INDIVIDUAL_RESULTS[user_language] % (student_name, student_result),
                                       parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
    else:
        print(f'Strange query data {query.data} in admin_exam_registration_finish', file=sys.stderr)

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
    keyboard.append([InlineKeyboardButton(messages.EXAM_ALL_RESULTS[user_language], callback_data=f"admin_all_students_results")])
    keyboard.append([InlineKeyboardButton(messages.EXAM_FINISH_REVIEW[user_language], callback_data=f"admin_finish_review_results")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages.EXAM_PER_STUDENT_RESULTS[user_language], reply_markup=reply_markup)

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
