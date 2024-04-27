import abc


class State(metaclass=abc.ABCMeta):
    def __init__(self, game):
        self.game = game
        self.prev_state = None

    @abc.abstractclassmethod
    def update(self, delta_time, actions):
        pass

    @abc.abstractclassmethod
    def render(self, display):
        pass

    def enter_state(self):
        if len(self.game.state_stack) > 1:
            self.prev_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)

    def exit_state(self):
        self.game.state_stack.pop()
