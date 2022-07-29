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
        self.image.fill( self.colour)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y

    def move(self, dx=0, dy=0):
        if self.x + dx >= 0 and self.x + dx < TILEWIDTH and self.y + dy >= 0 and self.y + dy < TILEWIDTH:      
            self.x += dx;
            self.y += dy;

    def update(self):
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE    

    def getX(self):
        return self.x

    def setX(self, x):
        self.x = x

    def getY(self):
        return self.y

    def setY(self, y):
        self.y = y

    def getColour(self):
        return self.colour

    def setColour(self, colour):
        self.colour = colour

    def getScore(self):
        return self.score

    def incrementScore(self):
        self.score += 1

    def decrementScore(self):
        self.score -= 1
    