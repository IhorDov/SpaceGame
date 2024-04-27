import os
import pygame
from random import randint
from pygame import mixer
from game_object import GameObject
from score import Score
from life import Life
from level import Level
from states.state import State
from states.menu import Menu


class GameWorld(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.game = game
        # Dowload background image
        self.download_background_img()
        self.enemy_speed = 50
        self.enemy_spawn_x = randint(
            0, self.game.GAME_WIDTH - 46)  # 46 is ENEMY_WIDTH
        self.space_ship_spawn_x = randint(
            0, self.game.GAME_WIDTH - 27)  # 27 is SPACE_SHIP_WIDTH
        self.space_ship_spawn_y = randint(-1600, -self.game.GAME_HEIGHT)
        self.meteor_spawn_y = -self.game.GAME_HEIGHT/2
        self.player = Player(self.game.GAME_WIDTH/2 - 23,
                             self.game.GAME_HEIGHT - 37.5, pygame.image.load(os.path.join(self.game.sprite_dir, "player", "player_front1.png")), self.game)
        self.meteor = Meteor(self.enemy_spawn_x, self.meteor_spawn_y, pygame.image.load(os.path.join(
            self.game.sprite_dir, 'meteors', 'meteorBrown.png')), self.game)
        self.space_ship = SpaceShip(self.space_ship_spawn_x, self.space_ship_spawn_y, pygame.image.load(os.path.join(
            self.game.sprite_dir, 'space_ships', 'space_ship.png')), self.game)
        self.enemy_index = randint(0, 3)
        self.enemy = Enemy(self.enemy_spawn_x, 0, pygame.image.load(os.path.join(
            self.game.sprite_dir, 'enemy', 'enemy' + str(self.enemy_index) + '.png')), self.game)
        self.move_down = 0
        self.laser = Laser(self.player.player_rect.x + self.player.player_width /
                           2 - 3, self.player.player_rect.y - 16, pygame.image.load(os.path.join(
                               self.game.assets_dir, 'map', 'laser.png')), game)
        self.laser_was_fired = False
        self.is_lost = False
        self.pos_x, self.pos_y = self.enemy.enemy_rect.x + \
            self.enemy.ENEMY_WIDTH/2 - 3, self.enemy.enemy_rect.y
        self.is_player_enemy_collision = False
        self.game_objects = pygame.sprite.Group()
        self.new_game_objects = pygame.sprite.Group()
        self.explosion_group = pygame.sprite.Group()
        self.damage_group = pygame.sprite.Group()
        self.new_game_objects.add(self.player)
        self.new_game_objects.add(self.meteor)
        self.new_game_objects.add(self.enemy)
        self.new_game_objects.add(self.space_ship)

        self.load_score()
        self.load_life()
        self.load_level()
        self.game_over_text = "Game Over!"
        self.scores = []

    def update(self, delta_time, actions):
        if actions['menu']:
            new_state = Menu(self.game)
            new_state.enter_state()
            mixer.music.pause()
        self.background_move()

        for game_object in self.new_game_objects:
            self.game_objects.add(game_object)
        self.new_game_objects.empty()

        self.shoot_laser(delta_time, actions)
        self.player_enemy_collision()
        self.laser_meteor_collion()
        self.update_explosion_position()
        self.update_damage_position()
        self.laser_enemy_collion(delta_time, actions)
        self.player_meteor_collision()
        self.player_space_ship_collision()
        self.explosion_group.update()
        self.damage_group.update()
        self.game_objects.update(delta_time, actions)
        self.update_score()
        self.update_life()
        self.update_level()

    def render(self, display):
        if not self.is_lost:
            self.render_background(display)

            for game_object in self.game_objects:
                game_object.render(display)
                if self.laser_was_fired:
                    for laser in self.player.lasers:
                        laser.render(display)
            self.explosion_group.draw(display)
            self.damage_group.draw(display)
            display.blit(self.game_score_text, (10, 10))
            display.blit(self.game_lives_text, (10, 30))
            display.blit(self.game_levels_text, (400, 10))
        else:
            display.fill((32, 52, 71))
            self.game.draw_text(display, self.game_over_text, pygame.Color('red'),
                                self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2)
        pygame.display.update()

    def update_damage_position(self):
        self.damage_pos_x, self.damage_pos_y = self.meteor.meteor_rect.x + \
            self.meteor.METEOR_WIDTH/2, self.meteor.meteor_rect.y

    def update_explosion_position(self):
        self.pos_x, self.pos_y = self.enemy.enemy_rect.x + \
            self.enemy.ENEMY_WIDTH/2 - 3, self.enemy.enemy_rect.y

    def update_score(self):
        self.game_score_text = self.game_score_font.render(
            f"Score: {Score._score}", True, 'green')

    def update_life(self):
        self.game_lives_text = self.game_lives_font.render(
            f"Lives: {Life._life}", True, 'green')

    def update_level(self):
        self.game_levels_text = self.game_levels_font.render(
            f"Level: {Level._level}", True, 'black')

    def laser_enemy_collion(self, delta_time, actions):
        for laser in self.player.lasers:
            if self.enemy.enemy_rect.x < laser.rect.x < self.enemy.enemy_rect.x + self.enemy.ENEMY_WIDTH - laser.laser_width and \
                    self.enemy.enemy_rect.y < laser.rect.y < self.enemy.enemy_rect.y + self.enemy.ENEMY_HEIGHT - laser.laser_height:
                self.enemy.enemy_rect.x, self.enemy.enemy_rect.y = randint(
                    0, self.game.GAME_WIDTH - 46), - self.enemy.ENEMY_HEIGHT

                laser.kill()
                explosion_sound = mixer.Sound("8bit_bomb_explosion.wav")
                explosion_sound.play()
                self.explosion_group.add(
                    Explosion(self.pos_x, self.pos_y, self.game))
                Score._score += 1

                self.scores.append(Score._score)

                for _ in self.scores:
                    if len(self.scores) == 10:
                        Life._life += 1
                        Level._level += 1
                        self.scores.clear()

    def laser_meteor_collion(self):
        for laser in self.player.lasers:
            if self.meteor.meteor_rect.x < laser.rect.x < self.meteor.meteor_rect.x + self.meteor.METEOR_WIDTH - laser.laser_width and \
                    self.meteor.meteor_rect.y < laser.rect.y < self.meteor.meteor_rect.y + self.meteor.METEOR_HEIGHT - laser.laser_height:
                laser.kill()

    def player_enemy_collision(self):
        if self.enemy.enemy_rect.colliderect(self.player.player_rect):
            self.enemy.enemy_rect.x, self.enemy.enemy_rect.y = randint(
                0, self.game.GAME_WIDTH - 46), - \
                self.enemy.ENEMY_HEIGHT
            self.is_player_enemy_collision = True
            if Life._life > 1:
                Life._life -= 1
                player_pain = mixer.Sound("player_pain.wav")
                player_pain.play()
            else:
                self.is_lost = True
                mixer.music.pause()
                mixer.Sound.stop

    def player_space_ship_collision(self):
        if self.space_ship.space_ship_rect.colliderect(self.player.player_rect):
            self.space_ship.space_ship_rect.x, self.space_ship.space_ship_rect.y = randint(
                0, self.game.GAME_WIDTH - 46), randint(-1600, -self.game.GAME_HEIGHT)
            if Life._life > 1:
                Life._life += 1
                live_sound = mixer.Sound("live_sound.wav")
                live_sound.play()
            else:
                mixer.music.pause()
                mixer.Sound("live_sound.wav").stop

    @property
    def get_player_enemy_collision(self):
        return self.is_player_enemy_collision

    def player_meteor_collision(self):
        if self.meteor.meteor_rect.colliderect(self.player.player_rect):
            self.meteor.meteor_rect.x, self.meteor.meteor_rect.y = randint(
                0, self.game.GAME_WIDTH - 46), -self.game.GAME_HEIGHT/2
            self.damage_group.add(
                Damage(self.damage_pos_x, self.damage_pos_y, self.game))

            meteor_damage = mixer.Sound("meteor_damage.wav")
            meteor_damage.play()

            if Life._life > 1:
                Life._life -= 1
            else:
                self.is_lost = True
                mixer.music.pause()
                mixer.Sound("meteor_damage.wav").stop

    def load_score(self):
        self.game_score_font = pygame.font.Font(None, 20)
        self.game_score_text = self.game_score_font.render(
            f"Score: {Score._score}", True, 'green')

    def load_life(self):
        self.game_lives_font = pygame.font.Font(None, 20)
        self.game_lives_text = self.game_lives_font.render(
            f"Lives: {Life._life}", True, 'green')

    def load_level(self):
        self.game_levels_font = pygame.font.Font(None, 20)
        self.game_levels_text = self.game_levels_font.render(
            f"Level: {Level._level}", True, 'black')

    def shoot_laser(self, delta_time, actions):
        if actions['shoot']:
            self.laser_was_fired = True
            if not self.is_lost:
                laser_sound = mixer.Sound("laser.wav")
                laser_sound.play()
        for laser in self.player.lasers:
            laser.update(delta_time, actions)

    def background_move(self):
        self.move_down += 0.5
        if self.move_down == self.game.SCREEN_HEIGHT:
            self.move_down = 0

    def download_background_img(self):
        # Dowload background image
        self.background_image = pygame.image.load(os.path.join(
            self.game.assets_dir, 'map', 'space.png')).convert()
        self.img_height = self.background_image.get_height()
        # Scale background image to the window
        self.background = pygame.transform.scale(
            self.background_image, (self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT))

    def render_background(self, display):
        display.blit(self.background, (0, self.move_down))
        display.blit(self.background,
                     (0, - self.game.SCREEN_HEIGHT + self.move_down))
        if self.move_down == self.game.SCREEN_HEIGHT:
            display.blit(self.background,
                         (0, - self.game.SCREEN_HEIGHT + self.move_down))


class Player(GameObject):
    def __init__(self, x, y, image, game):
        pygame.sprite.Sprite.__init__(self)
        GameObject.__init__(self, x, y, image)
        self.game = game
        self.load_sprites()
        self.image = self.curr_image
        # self.x, self.y = x, y
        self.player_width, self.player_height = self.curr_image.get_size()
        self.current_frame, self.last_frame_update = 0, 0
        self.player_rect = self.curr_image.get_rect(topleft=(x, y))
        self.player_speed = 200
        self.is_ready = True
        self.laser_time = 0
        self.laser_cooldown = 600  # We can shoot every 600 miliseconds
        self.lasers = pygame.sprite.Group()

    def update(self, delta_time, actions):
        # Get the direction from inputs
        direction_x = actions["right"] - actions["left"]
        direction_y = actions["down"] - actions["up"]
        # Update the position
        self.player_rect.x += self.player_speed * delta_time * direction_x
        self.player_rect.y += self.player_speed * delta_time * direction_y
        # Animate the sprite
        self.animate(delta_time, direction_x, direction_y)
        self.player_constraints()
        if actions['shoot'] and self.is_ready:
            self.lasers.add(
                Laser(self.player_rect.x + self.player_width/2 - 3, self.player_rect.y - 16, pygame.image.load(os.path.join(
                    self.game.assets_dir, 'map', 'laser.png')), self.game))
            self.is_ready = False
            self.laser_time = pygame.time.get_ticks()  # Uses just ones
        self.recharge_laser()
        self.update_player_speed()

    def recharge_laser(self):
        if not self.is_ready:
            current_time = pygame.time.get_ticks()  # It's will run continuously
            if current_time - self.laser_time >= self.laser_cooldown:
                self.is_ready = True

    def render(self, display):
        display.blit(self.curr_image, self.player_rect)
        pygame.display.update()

    def animate(self, delta_time, direction_x, direction_y):
        # Compute how much time has passed since the frame last updated
        self.last_frame_update += delta_time
        # If no direction is pressed, set image to idle and return
        if not (direction_x or direction_y):
            self.curr_image = self.curr_anim_list[0]
            return
        # If an image was pressed, use the appropriate list of frames according to direction
        if direction_x:
            if direction_x > 0:
                self.curr_anim_list = self.right_sprites
            else:
                self.curr_anim_list = self.left_sprites
        if direction_y:
            if direction_y > 0:
                self.curr_anim_list = self.back_sprites
            else:
                self.curr_anim_list = self.front_sprites
        # Advance the animation if enough time has elapsed
        if self.last_frame_update > .15:
            self.last_frame_update = 0
            self.current_frame = (self.current_frame +
                                  1) % len(self.curr_anim_list)
            self.curr_image = self.curr_anim_list[self.current_frame]

    def player_constraints(self):
        if self.player_rect.x < 0:
            self.player_rect.x = 0
        if self.player_rect.x + self.player_width > self.game.GAME_WIDTH:
            self.player_rect.x = self.game.GAME_WIDTH - self.player_width
        if self.player_rect.y < 0:
            self.player_rect.y = 0
        if self.player_rect.y + self.player_height > self.game.GAME_HEIGHT:
            self.player_rect.y = self.game.GAME_HEIGHT - self.player_height

    def load_sprites(self):
        # Get the diretory with the player sprites
        self.sprite_dir = os.path.join(self.game.sprite_dir, "player")
        self.front_sprites, self.back_sprites, self.right_sprites, self.left_sprites = [], [], [], []
        # Load in the frames for each direction
        for i in range(1, 5):
            self.front_sprites.append(pygame.image.load(os.path.join(
                self.sprite_dir, "player_front" + str(i) + ".png")))
            self.back_sprites.append(pygame.image.load(os.path.join(
                self.sprite_dir, "player_back" + str(i) + ".png")))
            self.right_sprites.append(pygame.image.load(os.path.join(
                self.sprite_dir, "player_right" + str(i) + ".png")))
            self.left_sprites.append(pygame.image.load(os.path.join(
                self.sprite_dir, "player_left" + str(i) + ".png")))
        # Set the default frames to facing front
        self.curr_image = self.front_sprites[0]
        self.curr_anim_list = self.front_sprites

    def update_player_speed(self):
        if Level._level == 5:
            self.player_speed = 400
        if Level._level == 10:
            self.player_speed = 800


class Laser(GameObject):
    def __init__(self, x, y, image, game):
        pygame.sprite.Sprite.__init__(self)
        GameObject.__init__(self, x, y, image)
        self.game = game
        # self.x, self.y = x, y
        self.load_laser_sprites()
        self.LASER_SPEED = 500
        self.rect = self.laser_image.get_rect(topleft=(x, y))

    def update(self, delta_time, actions):
        self.rect.y -= delta_time * self.LASER_SPEED
        if self.rect.y < - self.laser_height:
            self.kill()

    def render(self, display):
        display.blit(self.laser_image, self.rect)
        pygame.display.update()

    def load_laser_sprites(self):
        self.laser_image = pygame.image.load(os.path.join(
            self.game.assets_dir, 'map', 'laser.png'))
        self.laser_width, self.laser_height = self.laser_image.get_size()


class Enemy(GameObject):
    def __init__(self, x, y, image, game):
        pygame.sprite.Sprite.__init__(self)
        GameObject.__init__(self, x, y, image)
        self.game = game
        self.index = randint(0, 3)
        self.download_enemy_img()
        self.x, self.y = x, y
        self.enemy_rect = self.curr_enemy_image.get_rect(topleft=(x, y))
        self.ENEMY_WIDTH, self.ENEMY_HEIGHT = self.curr_enemy_image.get_size()
        self.enemy_speed = 50
        self.enemy_fps = 0

    def update(self, delta_time, actions):
        # self.curr_enemy_image = self.enemyImg[self.index]
        self.update_level()
        # Update the position
        self.update_enemy_position(delta_time)

    def update_enemy_position(self, delta_time):
        self.enemy_rect.y += delta_time * self.enemy_speed
        if self.enemy_rect.y > self.game.GAME_HEIGHT + self.ENEMY_HEIGHT:
            self.download_enemy_img()
            # self.curr_enemy_image = self.enemyImg[self.index]
            self.enemy_rect.y = - self.ENEMY_HEIGHT
            self.enemy_rect.x = randint(
                0, self.game.GAME_WIDTH - self.ENEMY_WIDTH)

    def update_level(self):
        if Level._level == 1:
            self.enemy_speed = 100
        if Level._level == 2:
            self.enemy_speed = 150
        if Level._level == 3:
            self.enemy_speed = 200
        if Level._level == 4:
            self.enemy_speed = 250
        if Level._level == 5:
            self.enemy_speed = 300
        if Level._level == 6:
            self.enemy_speed = 350
        if Level._level == 7:
            self.enemy_speed = 400
        if Level._level == 8:
            self.enemy_speed = 450
        if Level._level == 9:
            self.enemy_speed = 500
        if Level._level == 10:
            self.enemy_speed = 550

    def render(self, display):
        display.blit(self.curr_enemy_image, self.enemy_rect)
        pygame.display.update()

    def download_enemy_img(self):
        # Dowload enemy image
        self.enemyImg = []
        for i in range(1, 5):
            self.sprite_enemy_dir = os.path.join(self.game.sprite_dir, "enemy")
            self.enemyImg.append(pygame.image.load(os.path.join(
                self.sprite_enemy_dir, "enemy" + str(i) + ".png")))
        self.curr_enemy_image = self.enemyImg[self.index]


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.sprite_dir = os.path.join(self.game.sprite_dir, "explosion")
        self.images = []
        for num in range(1, 17):
            self.img = pygame.image.load(os.path.join(
                self.sprite_dir, "explosion" + str(num) + ".png"))
            self.img = pygame.transform.scale(self.img, (100, 100))
            self.images.append(self.img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 4
        # update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # if the animation is complete, reset animation index
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()


class Meteor(GameObject):
    def __init__(self, x, y, image, game):
        pygame.sprite.Sprite.__init__(self)
        GameObject.__init__(self, x, y, image)
        self.game = game
        self.download_meteor_img()
        self.meteor_rect = self.meteor_image.get_rect(topleft=(x, y))
        self.METEOR_SPEED = 80
        self.x = randint(0, self.game.GAME_WIDTH - self.METEOR_WIDTH)
        self.y = randint(-300, -self.METEOR_HEIGHT)

    def update(self, delta_time, actions):
        # Update the position
        self.meteor_rect.y += delta_time * self.METEOR_SPEED
        if self.meteor_rect.y > self.game.GAME_HEIGHT + self.METEOR_HEIGHT:
            self.meteor_rect.y = randint(-300, -self.METEOR_HEIGHT)
            self.meteor_rect.x = randint(
                0, self.game.GAME_WIDTH - self.METEOR_WIDTH)

    def render(self, display):
        display.blit(self.meteor_image, self.meteor_rect)
        pygame.display.update()

    def download_meteor_img(self):
        # Dowload meteor image
        self.meteor_image = pygame.image.load(os.path.join(
            self.game.sprite_dir, 'meteors', 'meteorBrown.png'))
        self.METEOR_WIDTH, self.METEOR_HEIGHT = self.meteor_image.get_size()


class Damage(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.sprite_dir = os.path.join(self.game.sprite_dir, "damage")
        self.damage_images = []
        for num in range(1, 6):
            self.damage_img = pygame.image.load(os.path.join(
                self.sprite_dir, "damage" + str(num) + ".png"))
            self.damage_img = pygame.transform.scale(
                self.damage_img, (50, 50))
            self.damage_images.append(self.damage_img)
        self.damage_index = 0
        self.image = self.damage_images[self.damage_index]
        self.rect = self.image.get_rect()
        self.DAMAGE_WIDTH, self.DAMAGE_HEIGHT = self.image.get_size()
        self.rect.center = [x, y]
        self.damage_counter = 0
        self.DAMAGE_SPEED = 1

    def update(self):
        damage_speed = 20  # It's 4 frames for second
        # update explosion animation
        self.damage_counter += 1

        if self.damage_counter >= damage_speed and self.damage_index < len(self.damage_images) - 1:
            self.damage_counter = 0
            self.damage_index += 1
            self.image = self.damage_images[self.damage_index]

        # if the animation is complete, reset animation index
        if self.damage_index >= len(self.damage_images) - 1 and self.damage_counter >= damage_speed:
            self.kill()

        if GameWorld.get_player_enemy_collision:
            self.rect.y += 1 * self.DAMAGE_SPEED
        if self.rect.y > self.game.GAME_HEIGHT + self.DAMAGE_HEIGHT:
            self.kill()


class SpaceShip(GameObject):
    def __init__(self, x, y, image, game):
        pygame.sprite.Sprite.__init__(self)
        GameObject.__init__(self, x, y, image)
        self.game = game
        self.download_space_ship_img()
        # self.x, self.y = x, y
        self.SPACE_SHIP_SPEED = 100
        self.x = randint(0, self.game.GAME_WIDTH - self.SPACE_SHIP_WIDTH)
        self.y = randint(-1600, -self.game.GAME_HEIGHT)
        self.space_ship_rect = self.space_ship_image.get_rect(topleft=(x, y))

    def update(self, delta_time, actions):
        # Update the position
        self.update_space_ship_position(delta_time)

    def update_space_ship_position(self, delta_time):
        self.space_ship_rect.y += delta_time * self.SPACE_SHIP_SPEED
        if self.space_ship_rect.y > self.game.GAME_HEIGHT + self.SPACE_SHIP_HEIGHT:
            self.space_ship_rect.y = randint(-1600, -self.game.GAME_HEIGHT)
            self.space_ship_rect.x = randint(
                0, self.game.GAME_WIDTH - self.SPACE_SHIP_WIDTH)

    def render(self, display):
        display.blit(self.space_ship_image, self.space_ship_rect)
        pygame.display.update()

    def download_space_ship_img(self):
        # Dowload enemy image
        self.space_ship_image = pygame.image.load(os.path.join(
            self.game.sprite_dir, 'space_ships', 'space_ship.png'))
        self.SPACE_SHIP_WIDTH, self.SPACE_SHIP_HEIGHT = self.space_ship_image.get_size()
