from enum import Enum
import random
class Colour(Enum):
    WHITE = 0
    BLACK = 1
    RED = 2
    BLUE = 3
    GREEN = 4
    YELLOW = 5
class Board:
    def __init__(self, height=0, width=0, timer=0):
        self.height = height
        self.width = width
        self.board = []
        self.timer = timer

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

    def initializeBoard(self):
        self.board = [[0 for i in range(self.height)]
                      for j in range(self.width)]

    def printBoard(self):
        print('\n'.join(' '.join(str(i) for i in row) for row in self.board))