import pygame
from pygame import mixer
from states.state import State
from states.game_world import GameWorld
# from states.menu import Menu


class Title(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.text1 = "Welcome to GameSpace"
        self.text2 = "To start game push Enter key"
        self.text3 = "To move player use WASD keys"
        self.text4 = "Use Menu - M/Backspace keys"
        self.text5 = "Up/Down keys - move cursor"
        self.text6 = "To leave the game - push Esc"

    def update(self, delta_time, actions):
        if actions['start']:
            new_state = GameWorld(self.game)
            new_state.enter_state()
            mixer.music.load('BlindShift.mp3')
            mixer.music.play(-1)
        # if actions['menu']:
        #     new_state = Menu(self.game)
        #     new_state.enter_state()
        self.game.reset_keys()

    def render(self, display):
        display.fill((32, 52, 71))
        self.game.draw_text(display, self.text1, pygame.Color('yellow'),
                            self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2 - 80)
        self.game.draw_text(display, self.text2, (255, 0, 0),
                            self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2 - 40)
        self.game.draw_text(display, self.text3, (200, 200, 200),
                            self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2 - 10)
        self.game.draw_text(display, self.text4, (0, 200, 100),
                            self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2 + 20)
        self.game.draw_text(display, self.text5, (0, 255, 255),
                            self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2 + 50)
        self.game.draw_text(display, self.text6, (0, 255, 0),
                            self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2 + 80)
