from time import sleep
from .Util import TILESIZE, TILEWIDTH, COLOURS, TILEHEIGHT

import pygame as pg
# https://www.youtube.com/watch?v=3UxnelT9aCo
class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y, colour_index):
        self.colour_index = colour_index
        self.score = 0
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE-1, TILESIZE-1))
        self.x = x
        self.y = y
        self.x_rect = 1
        self.y_rect = 1
        self.image.fill(COLOURS[self.colour_index])
        if self.x == TILEWIDTH-1:
            self.x_rect = self.x-15
        if self.y == TILEHEIGHT-1:
            self.y_rect = self.y-15
        self.rect = pg.draw.rect(self.image, "black", [self.x_rect,self.y_rect,30,30],1)
        print(self.x)
        print(self.y)

    def move(self, dx=0, dy=0):
        if 0 <= self.x + dx < TILEWIDTH and 0 <= self.y + dy < TILEWIDTH:
            self.x += dx
            self.y += dy

    def update(self):
        self.rect.x = (self.x * TILESIZE)+1
        self.rect.y = (self.y * TILESIZE)+1

    def get_x(self):
        return self.x

    def set_x(self, x):
        self.x = x

    def get_y(self):
        return self.y

    def set_y(self, y):
        self.y = y

    def get_colour(self):
        return COLOURS[self.colour_index]

    def set_colour(self, colour_index):
        self.colour_index = colour_index

    def get_colour_index(self):
        return self.colour_index

    def get_score(self):
        return self.score

    def increment_score(self):
        self.score += 1

    def decrement_score(self):
        self.score -= 1
