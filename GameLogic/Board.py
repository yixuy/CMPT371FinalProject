from enum import Enum
class Colour(Enum):
    WHITE = 0
    BLACK = 1
    RED = 2
    BLUE = 3
    GREEN = 4
    YELLOW = 5
class Board:
    def __init__(self):
        self.height = 0
        self.width = 0
        self.timer = 0
        self.colour = Colour.Colour()

    def getHeight(self):
        return self.height

    def setHeight(self, height):
        self.height = height

    def getWidth(self):
        return self.width

    def setWidth(self, width):
        self.width = width

    def getTime(self):
        return self.timer
