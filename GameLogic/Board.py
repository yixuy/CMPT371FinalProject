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
        newBoard = [[0 for i in range(self.height)] for j in range(self.width)]
        n_walls = int(self.height * self.width * 0.2)
        for i in range(n_walls):
            row = random.randint(0, self.height-1)
            newBoard[random.randint(0, self.height-1)][random.randint(0, self.width-1)] = Colour.BLACK
        self.board = newBoard

    def printBoard(self):
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row][col] == Colour.BLACK:
                    print(self.board[row][col].value, end = ' ')
                else:
                    print(self.board[row][col], end = ' ')
            print()