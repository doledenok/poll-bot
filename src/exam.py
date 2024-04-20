class Exam:
    def __init__(self, id: int):
        self.id = id
        self.speakers = []

    def add_speaker(self, name: str):
        self.speakers.append(name)

    def get_speaker_names(self, name: str = "") -> list:
        """
        Если педерается параметр name - возвращаем все имена кроме этого.
        """
        if not name:
            return self.speakers
        without_one_speakers = []
        for speaker in self.speakers:
            if speaker != name:
                without_one_speakers.append(speaker)
        return without_one_speakers
