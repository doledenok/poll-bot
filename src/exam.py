import os
import enum
import csv
from typing import List, Dict


class ExamStatus(enum.Enum):
    Created = 0
    RegistrationFinished = 1
    PresentationsFinished = 2
    ResultsReviewFinished = 3

class ExaminatedSkills(enum.Enum):
    CalmnessStory = 0
    CalmnessQuestions = 1
    EyeContactStory = 2
    EyeContactQuesitons = 3
    AnswerSkill = 4
    Notes = 5

class Exam:
    def __init__(self, id: int):
        self.exam_id = id
        self.speaker_names: List[str] = []
        self.speaker_answers: List[Dict[int, dict]] = []
        self.exam_status: ExamStatus = ExamStatus.Created

    def add_speaker(self, name: str) -> int | None:
        """
        Return participant id or None if name is not unique.
        """
        if name in self.speaker_names:
            return None
        self.speaker_names.append(name)
        self.speaker_answers.append({})
        return len(self.speaker_names) - 1

    def get_speaker_names(self, speaker_id: int = None) -> list:
        """
        If speaker_id is not None return all speaker names except speaker with that id.
        """
        if speaker_id is None:
            return self.speaker_names
        without_one_speakers = self.speaker_names[:speaker_id]
        if speaker_id >= len(self.speaker_names) - 1:
            return without_one_speakers
        return without_one_speakers + self.speaker_names[speaker_id+1:]

    def get_name_by_id(self, speaker_id: int) -> str:
        return self.speaker_names[speaker_id] # если вдруг слишком большой id - пусть падает

    def add_answer(self, listener_id: int, speaker_id: int, field: str, value: int | str):
        """
        Store score of some criteria for listener and speaker.
        Criteria are:
        - calmness_story
        - calmness_questions
        - eye_contact_story
        - eye_contact_quesitons
        - answer_skill
        - notes
        """
        print(listener_id, speaker_id, field, value)
        if speaker_id not in self.speaker_answers[listener_id]:
            self.speaker_answers[listener_id][speaker_id] = {}
        self.speaker_answers[listener_id][speaker_id][field] = value

    def save_results(self, exams_csv_db: str) -> None:
        saved_rows = 0
        with open(exams_csv_db, 'a+', newline='') as csvfile:
            fieldnames = ['exam_id', 'answering_student_id', 'listening_student_id', 'question_id', 'student_mark']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if os.path.getsize(exams_csv_db) == 0:
                writer.writeheader()
            for listener_id in range(len(self.speaker_answers)):
                for speaker_id in self.speaker_answers[listener_id]:
                    for field in self.speaker_answers[listener_id][speaker_id]:
                        writer.writerow({
                            'exam_id': self.exam_id,
                            'answering_student_id': speaker_id,
                            'listening_student_id': listener_id,
                            'question_id': field,
                            'student_mark': self.speaker_answers[listener_id][speaker_id][field]
                        })
                        saved_rows += 1
        return saved_rows
