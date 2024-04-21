import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.figure
from typing import List, Dict
import os

def plot_student_results(student_name: str, questions: List[str], scores: List[float]) -> matplotlib.figure.Figure:
    fig, ax1 = plt.subplots(figsize=(9, 7), layout='constrained')
    fig.canvas.manager.set_window_title('Eldorado K-8 Fitness Chart')

    ax1.set_title(student_name)
    ax1.set_xlabel('Per-question student result from 0 to 10', fontsize=18)

    rects = ax1.barh(questions, scores, align='center', height=0.5)

    large_scores = [p if p > 5 else '' for p in scores]
    small_scores = [p if p <= 5 else '' for p in scores]
    ax1.bar_label(rects, small_scores,
                  padding=5, color='black', fontweight='bold')
    ax1.bar_label(rects, large_scores,
                  padding=-32, color='white', fontweight='bold')

    ax1.set_xlim([0, 10])
    ax1.set_xticks([i for i in range(10)])
    ax1.xaxis.grid(True, linestyle='--', which='major',
                   color='grey', alpha=.25)
    ax1.axvline(50, color='grey', alpha=0.25)

    return fig

def calculate_individual_stats(exam_user_marks_df: pd.DataFrame) -> pd.DataFrame:
    per_question_user_marks = exam_user_marks_df.loc[:, ('question_id', 'student_mark')].groupby(by='question_id')
    mean_per_question_user_marks = per_question_user_marks.mean().rename(columns={'student_mark': 'mean_student_mark'})
    median_per_question_user_marks = per_question_user_marks.median().rename(columns={'student_mark': 'median_student_mark'})
    std_per_question_user_marks = per_question_user_marks.std().rename(columns={'student_mark': 'std_student_mark'})
    cnt_per_question_user_marks = per_question_user_marks.count().rename(columns={'student_mark': 'cnt_student_mark'})

    per_question_exam_stats = pd.concat((mean_per_question_user_marks, median_per_question_user_marks, std_per_question_user_marks,cnt_per_question_user_marks ), axis=1)
    return per_question_exam_stats
    

def calculate_exam_stats(exam_id: int, exam_marks_csv: str, stats_global_csv_db: str) -> None:
    exam_marks_df = pd.read_csv(exam_marks_csv)

    relevant_exam_df = exam_marks_df.loc[exam_marks_df.exam_id == exam_id]

    examinee_users = relevant_exam_df.answering_student_id.unique()
    exam_user_marks_groups = relevant_exam_df.groupby(by='answering_student_id')
    for user_id in examinee_users:
        user_per_question_exam_stats = calculate_individual_stats(exam_user_marks_groups.get_group(user_id))
        user_per_question_exam_stats['exam_id'] = exam_id
        user_per_question_exam_stats['user_id'] = user_id
        user_per_question_exam_stats.to_csv(stats_global_csv_db, mode='a+', header=not os.path.exists(stats_global_csv_db))

def get_exam_results(exam_id: int, stats_global_csv_db: str) -> Dict[int, str]:
    exam_stats_df = pd.read_csv(stats_global_csv_db)
    relevant_resutls = exam_stats_df[exam_stats_df['exam_id'] == exam_id]
    per_user_relevant_resutls = relevant_resutls.groupby(by='user_id')
    user_ids = per_user_relevant_resutls.groups.keys()
    per_user_markdown_results = dict()
    for user_id in user_ids:
        user_relevant_results = per_user_relevant_resutls.get_group(user_id)
        user_plot_results_figure = plot_student_results(user_id, 
                             list(user_relevant_results.question_id.values.flatten()), 
                             list(user_relevant_results.mean_student_mark.values.flatten()))
        user_plot_results_figure.savefig(f'{stats_global_csv_db}_{exam_id}_{user_id}_results.png')
        per_user_markdown_results[user_id] = user_relevant_results.sort_values(by='question_id', axis=0).to_markdown()

    return per_user_markdown_results

def get_student_results(exam_id: int, student_id: int, stats_global_csv_db: str) -> str:
    exam_stats_df = pd.read_csv(stats_global_csv_db)
    student_all_results = exam_stats_df[exam_stats_df['user_id'] == student_id]
    relevant_resutls = student_all_results[student_all_results['exam_id'] == exam_id]
    user_plot_results_figure = plot_student_results(student_id, 
                                                    list(relevant_resutls.question_id.values.flatten()), 
                                                    list(relevant_resutls.mean_student_mark.values.flatten()))
    user_plot_results_figure.savefig(f'{stats_global_csv_db}_{exam_id}_{user_id}_results.png')

    #### TODO: реализовать графики с прогрессом, когда накопится история сдач
    # per_question_student_results = student_all_results.groupby(by='question_id')
    # question_ids = per_question_student_results.groups.keys()
    # for question_id in question_ids:
    #     question_student_results = per_question_student_results.get_group(question_id)
    #     sorted_question_student_results = question_student_results.sort_values(by='exam_id', axis=0)
    #################

    return relevant_resutls.to_markdown()
