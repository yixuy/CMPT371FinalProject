import random
# from util import *

class Board:
    def __init__(self, columns=0, rows=0):
        self.columns = columns
        self.rows = rows
        self.board = []

    def getcolumns(self):
        return self.columns

    def setcolumns(self, columns):
        self.columns = columns

    def getrows(self):
        return self.rows

    def setrows(self, rows):
        self.rows = rows

    # Cell Type 0: 1x1 cell
    # Cell Type 1: 1x2 cell
    # Cell Type 2: 2x1 cell
    def setCellType0(self, x_coord, y_coord):
        self.board[y_coord+1][x_coord] = 0
        self.board[y_coord][x_coord+1] = 0
        self.board[y_coord-1][x_coord] = 0
        self.board[y_coord][x_coord-1] = 0
        self.board[y_coord+1][x_coord+1] = 0
        self.board[y_coord-1][x_coord-1] = 0
        self.board[y_coord+1][x_coord-1] = 0
        self.board[y_coord-1][x_coord+1] = 0

    def setCellType1(self, x_coord, y_coord):
        self.board[y_coord+1][x_coord] = -1
        self.board[y_coord+1][x_coord+1] = 0
        self.board[y_coord+1][x_coord-1] = 0
        self.board[y_coord+2][x_coord] = 0
        self.board[y_coord][x_coord+1] = 0
        self.board[y_coord-1][x_coord] = 0
        self.board[y_coord][x_coord-1] = 0
        self.board[y_coord+2][x_coord+1] = 0
        self.board[y_coord-1][x_coord-1] = 0
        self.board[y_coord+2][x_coord-1] = 0
        self.board[y_coord-1][x_coord+1] = 0

    def setCellType2(self, x_coord, y_coord):
        self.board[y_coord][x_coord + 1] = -1
        self.board[y_coord+1][x_coord] = 0
        self.board[y_coord][x_coord+2] = 0
        self.board[y_coord-1][x_coord] = 0
        self.board[y_coord][x_coord-1] = 0
        self.board[y_coord+1][x_coord+2] = 0
        self.board[y_coord-1][x_coord-1] = 0
        self.board[y_coord+1][x_coord-1] = 0
        self.board[y_coord-1][x_coord+2] = 0
        self.board[y_coord-1][x_coord+1] = 0
        self.board[y_coord+1][x_coord+1] = 0


    def getBoard(self):
        return  self.board;

    def getItem(self, x, y):
        return  self.board[x][y];

    def initializeBoard(self):
        self.board = [[0 for i in range(self.columns)] for j in range(self.rows)]
        n_walls = int(self.columns * self.rows * 0.3)
        for i in range(n_walls):
            cellType = random.randint(0,2)
            random_Y = random.randint(0, self.rows-1)
            random_X = random.randint(0, self.columns-1)
            if(random_Y != 0 and random_X != 0 and random_Y != self.rows-1 and random_X != self.columns-1):
                self.board[random_Y][random_X] = -1
                if(cellType == 0):
                    self.setCellType0(random_X, random_Y)
                elif(cellType == 1 and random_Y < self.rows-2):
                    self.setCellType1(random_X,random_Y)
                elif(cellType == 2 and random_X < self.columns-2):
                    self.setCellType2(random_X,random_Y)
                else:
                    self.board[random_Y][random_X] = 0
            print("Cell type is:" + str(cellType))
            print("random_Y is:" + str(random_Y))
            print("random_X is:" + str(random_X))
            self.printBoard()
            print()


    def printBoard(self):
        print('\n'.join(' '.join('{0: ^3}'.format(str(i)) for i in row) for row in self.board))