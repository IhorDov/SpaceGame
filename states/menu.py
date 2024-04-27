import pygame
import os
from states.state import State
from pygame import mixer

from score import Score


class Menu(State):
    def __init__(self, game):
        self.game = game
        State.__init__(self, game)
        # Set the menu
        self.menu_img = pygame.image.load(os.path.join(
            self.game.assets_dir, 'map', 'menu.png'))
        self.menu_rect = self.menu_img.get_rect()
        self.menu_rect.center = (
            self.game.GAME_WIDTH * 0.5, self.game.GAME_HEIGHT * 0.4)
        # Set the cursor and menu states
        self.menu_options = {0: 'Resume', 1: 'Options', 2: 'Exit'}
        self.index = 0
        # Variables for the cursor
        self.cursor_img = pygame.image.load(os.path.join(
            self.game.assets_dir, 'map', 'cursor.png'))
        self.cursor_rect = self.cursor_img.get_rect()
        self.cursor_pos_y = self.menu_rect.y + 108
        self.cursor_rect.x, self.cursor_rect.y = self.menu_rect.x + 80, self.cursor_pos_y

    def update(self, delta_time, actions):
        self.update_cursor(actions)
        if actions['start']:
            self.transition_state()

        if actions['back']:
            self.exit_state()
            mixer.music.play()
        self.game.reset_keys()

    def render(self, display):
        display.blit(self.menu_img, self.menu_rect)
        display.blit(self.cursor_img, self.cursor_rect)

    def update_cursor(self, actions):
        if actions['cur_down']:
            self.index = (self.index + 1) % len(self.menu_options)
        elif actions['cur_up']:
            self.index = (self.index - 1) % len(self.menu_options)
        self.cursor_rect.y = self.cursor_pos_y + (self.index * 32)

    def transition_state(self):
        if self.menu_options[self.index] == 'Resume':
            new_state = Resume(self.game)
            new_state.enter_state()
        elif self.menu_options[self.index] == 'Options':
            pass
        # TO DO
        elif self.menu_options[self.index] == 'Exit':
            new_state = Exit(self.game)
            new_state.enter_state()
            # Exit()


class Resume(State):
    def __init__(self, game):
        self.game = game
        State.__init__(self, game)

    def update(self, delta_time, actions):
        if actions['back']:
            self.exit_state()

        self.game.reset_keys()

    def render(self, display):
        display.fill((255, 255, 255))
        self.game.draw_text(display, f"Your score is: {Score._score}", (0, 0, 0),
                            self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2)


class Exit(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.game = game
        self.text = "Thanks for playing!"

    def update(self, delta_time, actions):
        pygame.time.wait(3000)
        pygame.display.quit()
        self.game.running = False
        self.game.playing = False

    def render(self, display):
        display.fill((32, 52, 71))
        self.game.draw_text(display, self.text, pygame.Color('yellow'),
                            self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2)
