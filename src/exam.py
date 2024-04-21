from typing import List, Dict

class Exam:
    def __init__(self, id: int):
        self.exam_id = id
        self.speaker_names: List[str] = []
        self.speaker_answers: List[Dict[int, dict]] = []

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
        if speaker_id not in self.speaker_answers[listener_id]:
            self.speaker_answers[listener_id][speaker_id] = {}
        self.speaker_answers[listener_id][speaker_id][field] = value
