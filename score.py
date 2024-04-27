class Score():
    _score = 0

    def __init__(self, score):
        self._score = score

    @property
    def get_text(self):
        return self._score

    def set_text(self, value):
        self._score = value
