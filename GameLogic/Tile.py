from enum import Enum
class Colour(Enum):
    WHITE = 0
    BLACK = 1
    RED = 2
    BLUE = 3
    GREEN = 4
    YELLOW = 5
class Tile:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.colour = None

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
