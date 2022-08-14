import random
from .Util import *
# from util import *

class Board:
    def __init__(self, columns=0, rows=0):
        self.columns = columns
        self.rows = rows
        self.board = []
        self.white_tiles = 0

    def get_columns(self):
        return self.columns

    def set_columns(self, columns):
        self.columns = columns

    def get_rows(self):
        return self.rows

    def set_rows(self, rows):
        self.rows = rows

    def set_cell(self, x_coord, y_coord, color):
        self.board[x_coord][y_coord] = color

    # Cell Type 0: 1x1 cell
    # Cell Type 1: 1x2 cell
    # Cell Type 2: 2x1 cell

    def set_cell_type0(self, x_coord, y_coord):
        self.board[y_coord+1][x_coord] = 0
        self.board[y_coord][x_coord+1] = 0
        self.board[y_coord-1][x_coord] = 0
        self.board[y_coord][x_coord-1] = 0
        self.board[y_coord+1][x_coord+1] = 0
        self.board[y_coord-1][x_coord-1] = 0
        self.board[y_coord+1][x_coord-1] = 0
        self.board[y_coord-1][x_coord+1] = 0

    def set_cell_type1(self, x_coord, y_coord):
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

    def set_cell_type2(self, x_coord, y_coord):
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

    def get_board(self):
        return self.board

    def get_item(self, x, y):
        return self.board[x][y]

    def set_cell_colour_number(self,x,y,num):
        self.board[x][y] = num
    
    def count_number_of_white_tiles(self):
        black_tiles = 0
        for row in range(self.rows):
            for col in range(self.columns):
                if(self.get_item(row, col) == -1):
                    black_tiles += 1
        self.white_tiles =  int(WIDTH/TILESIZE * HEIGHT/TILESIZE - black_tiles)

    def decrement_white_tiles_loop(self, num_players):
        for i in range(num_players):
            self.decrement_white_tile()

    def decrement_white_tile(self):
        self.white_tiles -= 1

    def get_number_of_white_tiles(self):
        return self.white_tiles

    def initialize_board(self):
        self.board = [[0 for i in range(self.columns)] for j in range(self.rows)]
        black_tiles = 0
        n_walls = int(self.columns * self.rows * 0.3)
        for i in range(n_walls):
            cellType = random.randint(0,2)
            random_Y = random.randint(0, self.rows-1)
            random_X = random.randint(0, self.columns-1)
            if(random_Y != 0 and random_X != 0 and random_Y != self.rows-1 and random_X != self.columns-1):
                self.board[random_Y][random_X] = -1
                if(cellType == 0):
                    self.set_cell_type0(random_X, random_Y)
                elif(cellType == 1 and random_Y < self.rows-2):
                    self.set_cell_type1(random_X,random_Y)
                elif(cellType == 2 and random_X < self.columns-2):
                    self.set_cell_type2(random_X,random_Y)
                else:
                    self.board[random_Y][random_X] = 0
        self.count_number_of_white_tiles()
        print("NUMBER OF WHITE TILES:", self.white_tiles)

    def print_board(self):
        transpose_board = [[row[i] for row in self.board] for i in range(len(self.board[0]))]
        print('\n'.join(' '.join('{0: ^3}'.format(str(i)) for i in row) for row in transpose_board))

    # Called by Server
    def change_tile(self,x, y, colour_index):
        target = self.get_item(x,y)
        if(target == 0):
            self.set_cell_colour_number(x,y,colour_index)

    def print_this_board(board):
        transpose_board = [[row[i] for row in board] for i in range(len(board[0]))]
        print('\n'.join(' '.join('{0: ^3}'.format(str(i)) for i in row) for row in transpose_board))

    def is_filled(self):
        if self.get_number_of_white_tiles() == 0:
            return True
        return False

    def get_scores(self, player_nums):
        scores = {}
        for i in range(1, player_nums+1):
            scores[i] = 0
        for row in range(self.rows):
            for col in range(self.columns):
                if(self.get_item(row, col) == 1):
                    scores[1] += 1
                if(self.get_item(row, col) == 2):
                    scores[2] += 1
                if(self.get_item(row, col) == 3):
                    scores[3] += 1
                if(self.get_item(row, col) == 4):
                    scores[4] += 1
        return scores