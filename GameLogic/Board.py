import random
# from util import *

class Board:
    def __init__(self, height=0, width=0):
        self.height = height
        self.width = width
        self.board = []

    def getHeight(self):
        return self.height

    def setHeight(self, height):
        self.height = height

    def getWidth(self):
        return self.width

    def setWidth(self, width):
        self.width = width

    def getBoard(self):
        return  self.board;
    
    def getItem(self, x, y):
        return  self.board[x][y];

    def initializeBoard(self):
        newBoard = [[0 for i in range(self.height)] for j in range(self.width)]
        n_walls = int(self.height * self.width * 0.2)
        for i in range(n_walls):
            row = random.randint(0, self.height-1)
            newBoard[random.randint(0, self.height-1)][random.randint(0, self.width-1)] = -1
        self.board = newBoard

    def printBoard(self):
        print('\n'.join(' '.join(str(i) for i in row) for row in self.board))