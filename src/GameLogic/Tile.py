import pygame as pg

from .Util import *


# Adapted from: https://www.youtube.com/watch?v=3UxnelT9aCo
class Tile(pg.sprite.Sprite):
    def __init__(self, game, x, y, colour):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.x = x
        self.y = y
        self.colour = colour
        self.image = pg.Surface((TILESIZE-1, TILESIZE-1))
        self.image.fill(COLOURS[self.colour])
        self.rect = self.image.get_rect()
        self.rect.x = (self.x * TILESIZE)+1
        self.rect.y = (self.y * TILESIZE)+1

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def set_colour(self, colour_index):
        self.image.fill(COLOURS[colour_index])
        self.colour = colour_index
