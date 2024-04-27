class Level():
    _level = 0

    def __init__(self, level):
        self._level = level

    @property
    def get_text(self):
        return self._level

    def set_text(self, value):
        self._level = value
