import random


# from util import *

class Board:
    def __init__(self, height=0, width=0):
        self.height = height
        self.width = width
        self.board = []

    def get_height(self):
        return self.height

    def set_height(self, height):
        self.height = height

    def get_width(self):
        return self.width

    def set_width(self, width):
        self.width = width

    # Cell Type 0: 1x1 cell
    # Cell Type 1: 1x2 cell
    # Cell Type 2: 2x1 cell
    def set_cell(self, x_coord, y_coord):
        self.board[y_coord + 1][x_coord] = 0
        self.board[y_coord][x_coord + 1] = 0
        self.board[y_coord - 1][x_coord] = 0
        self.board[y_coord][x_coord - 1] = 0
        self.board[y_coord + 1][x_coord + 1] = 0
        self.board[y_coord - 1][x_coord - 1] = 0
        self.board[y_coord + 1][x_coord - 1] = 0
        self.board[y_coord - 1][x_coord + 1] = 0

    def get_board(self):
        return self.board;

    def get_item(self, x, y):
        return self.board[x][y];

    def initialize_board(self):
        self.board = [[0 for i in range(self.height)] for j in range(self.width)]
        n_walls = int(self.height * self.width * 0.2)
        for i in range(n_walls):
            # cellType = random.randint(0,2)
            random_Y = random.randint(0, self.width - 1)
            random_X = random.randint(0, self.height - 1)
            self.board[random_Y][random_X] = -1
            if random_Y // 2 != 0:
                if random_Y != 0 and random_X != 0 and random_Y != self.height - 1 and random_X != self.width - 1:
                    self.set_cell(random_X, random_Y)

    def print_board(self):
        print('\n'.join(' '.join('{0: ^3}'.format(str(i)) for i in row) for row in self.board))
