class Life():
    _life = 5

    def __init__(self, life):
        self._life = life

    @property
    def get_text(self):
        return self._life

    def set_text(self, value):
        self._life = value
