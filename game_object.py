import pygame
import abc


class GameObject(pygame.sprite.Sprite, metaclass=abc.ABCMeta):
    def __init__(self, x, y, image: pygame.Surface):
        pygame.sprite.Sprite.__init__(self)
        # self.x, self.y = x, y
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))

    @abc.abstractclassmethod
    def update(self, delta_time, actions):
        pass

    def render(self, display):
        display.blit(self.image, self.rect)
