import pandas

def calculate_individual_stats(exam_user_marks_df):
    per_question_user_marks = exam_user_marks_df.loc[:, ('question_id', 'student_mark')].groupby(by='question_id')
    mean_per_question_user_marks = per_question_user_marks.mean(skipna=True).rename(columns={'student_mark': 'mean_student_mark'})
    median_per_question_user_marks = per_question_user_marks.median(skipna=True).rename(columns={'student_mark': 'median_student_mark'})
    std_per_question_user_marks = per_question_user_marks.std(skipna=True).rename(columns={'student_mark': 'std_student_mark'})
    cnt_per_question_user_marks = per_question_user_marks.count(skipna=True).rename(columns={'student_mark': 'cnt_student_mark'})

    per_question_exam_stats = pd.concat((mean_per_question_user_marks, median_per_question_user_marks, std_per_question_user_marks,cnt_per_question_user_marks ), axis=1)
    return per_question_exam_stats
    

def calculate_exam_stats(exam_id, exam_marks_csv, stats_global_csv_db):
    exam_marks_df = pd.read_csv(exam_marks_csv)

    relevant_exam_df = exam_marks_df.loc[exam_marks_df.exam_id == exam_id]

    examinee_users = relevant_exam_df.answering_student_id.unique().values
    exam_user_marks_groups = relevant_exam_df.groupby(by='answering_student_id')
    for user_id in examinee_users:
        user_per_question_exam_stats = usercalculate_individual_stats(exam_user_marks_groups.get_group(user_id))
        user_per_question_exam_stats['exam_id'] = exam_id
        user_per_question_exam_stats['user_id'] = user_id
        user_per_question_exam_stats.to_csv(stats_global_csv_db, mode='a', header=False)
        







