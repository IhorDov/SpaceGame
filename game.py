import os
import pygame
import time
import sys
import server

from states.title import Title

'''Place to main Game class'''


class Game():
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('SpaceGame')
        # It's game resolution 480 x 270 pixels
        self.GAME_WIDTH, self.GAME_HEIGHT = 480, 270
        # Her define we screen with and screen height
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 1060, 620
        # We desided how we will draw game objects
        self.game_canvas = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))  # Her was maded size of the screen
        # Bool variables for running the game and about player is playing
        self.running, self.playing = True, True
        self.delta_time, self.previous_time = 0, 0

        self.actions = {'left': False, 'right': False, 'up': False,
                        'down': False, 'start': False, 'menu': False, 'back': False,
                        'shoot': False, 'cur_up': False, 'cur_down': False}  # Dictionary for moving and starting the game
        self.delta_time, self.previous_time = 0, 0  # Her setter we game time
        self.state_stack = []  # Empty list for at choise game states
        self.load_assets()
        self.load_states()

    def game_loop(self):  # Main game loop
        while self.playing:
            self.get_delta_time()
            self.get_events()
            self.update()
            self.render()
            self.clock.tick(60)

    def get_events(self):  # Main game events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Events for runing and playing the game
                self.playing = False
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:  # Events for keys input
                if event.key == pygame.K_ESCAPE:
                    self.playing = False
                    self.running = False
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_a:
                    self.actions['left'] = True
                if event.key == pygame.K_d:
                    self.actions['right'] = True
                if event.key == pygame.K_w:
                    self.actions['up'] = True
                if event.key == pygame.K_s:
                    self.actions['down'] = True
                if event.key == pygame.K_RETURN:
                    self.actions['start'] = True
                if event.key == pygame.K_BACKSPACE:
                    self.actions['back'] = True
                if event.key == pygame.K_m:
                    self.actions['menu'] = True
                if event.key == pygame.K_UP:
                    self.actions['cur_up'] = True
                if event.key == pygame.K_DOWN:
                    self.actions['cur_down'] = True
                if event.key == pygame.K_SPACE:
                    self.actions['shoot'] = True
            if event.type == pygame.KEYUP:  # Events when we don't use keys input
                if event.key == pygame.K_a:
                    self.actions['left'] = False
                if event.key == pygame.K_d:
                    self.actions['right'] = False
                if event.key == pygame.K_w:
                    self.actions['up'] = False
                if event.key == pygame.K_s:
                    self.actions['down'] = False
                if event.key == pygame.K_RETURN:
                    self.actions['start'] = False
                if event.key == pygame.K_BACKSPACE:
                    self.actions['back'] = False
                if event.key == pygame.K_m:
                    self.actions['menu'] = False
                if event.key == pygame.K_UP:
                    self.actions['cur_up'] = False
                if event.key == pygame.K_DOWN:
                    self.actions['cur_down'] = False
                if event.key == pygame.K_SPACE:
                    self.actions['shoot'] = False

    def update(self):
        self.state_stack[-1].update(self.delta_time, self.actions)

    def render(self):
        self.game_canvas.fill((32, 52, 71))
        self.state_stack[-1].render(self.game_canvas)
        if self.playing:
            self.screen.blit(pygame.transform.scale(
                self.game_canvas, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)), (0, 0))  # We draw game_canvas her
            # Draw background
            pygame.display.flip()

    def get_delta_time(self):
        now = pygame.time.get_ticks()
        self.delta_time = (now - self.previous_time) / 1000  # Get it in sec
        self.previous_time = now

    # Function to draw text on the screen
    def draw_text(self, surface, text, color, x_position, y_position):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x_position, y_position)
        surface.blit(text_surface, text_rect)

    def load_assets(self):
        # Create pointers to directories
        self.assets_dir = os.path.join('assets')
        self.sprite_dir = os.path.join(self.assets_dir, 'sprites')
        self.font_dir = os.path.join(self.assets_dir, 'font')
        self.font = pygame.font.Font(os.path.join(
            self.font_dir, "PressStart2P-vaV7.ttf"), 15)

    def load_states(self):
        self.title_screen = Title(self)
        self.state_stack.append(self.title_screen)

    def reset_keys(self):
        for action in self.actions:
            self.actions[action] = False


'''Enter point to the game'''

if __name__ == '__main__':
    g = Game()
    while g.running:
        g.game_loop()

    # server.receive()
