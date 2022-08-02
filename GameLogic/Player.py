from time import sleep
from util import TILESIZE, TILEWIDTH
import pygame as pg


# https://www.youtube.com/watch?v=3UxnelT9aCo

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y, color):
        self.colour = color
        self.score = 0
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(self.colour)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y

    def move(self, dx=0, dy=0):
        if 0 <= self.x + dx < TILEWIDTH and 0 <= self.y + dy < TILEWIDTH:
            self.x += dx
            self.y += dy

    def update(self):
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE

    def get_x(self):
        return self.x

    def set_x(self, x):
        self.x = x

    def get_y(self):
        return self.y

    def set_y(self, y):
        self.y = y

    def get_colour(self):
        return self.colour

    def set_colour(self, colour):
        self.colour = colour

    def get_score(self):
        return self.score

    def increment_score(self):
        self.score += 1

    def decrement_score(self):
        self.score -= 1
