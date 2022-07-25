from util import COLOURS, TILESIZE
class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.colour = None
        self.score = 0

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
