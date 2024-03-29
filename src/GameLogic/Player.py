import pygame as pg

from .Util import TILESIZE, TILEWIDTH, COLOURS, TILEHEIGHT


# Adapted from: https://www.youtube.com/watch?v=3UxnelT9aCo
class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y, colour_index):
        self.colour_index = colour_index
        self.score = 0
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE - 1, TILESIZE - 1))
        self.x = x
        self.y = y
        self.image.fill(COLOURS[self.colour_index])
        self.rect = pg.draw.rect(self.image, "black", [1, 1, 30, 30], 1)

    def move(self, dx=0, dy=0):
        if 0 <= self.x + dx < TILEWIDTH and 0 <= self.y + dy < TILEHEIGHT:
            self.x += dx
            self.y += dy

    def update(self):
        self.rect.x = (self.x * TILESIZE) + 1
        self.rect.y = (self.y * TILESIZE) + 1

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y
