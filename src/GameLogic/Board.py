import random


class Board:
    def __init__(self, columns=0, rows=0):
        self.columns = columns
        self.rows = rows
        self.board = []

    def get_columns(self):
        return self.columns

    def set_columns(self, columns):
        self.columns = columns

    def get_rows(self):
        return self.rows

    def set_rows(self, rows):
        self.rows = rows

    def set_cell(self, x_coord, y_coord, color):
        self.board[y_coord][x_coord] = color

    def set_cell_type0(self, x_coord, y_coord):
        self.board[y_coord + 1][x_coord] = 0
        self.board[y_coord][x_coord + 1] = 0
        self.board[y_coord - 1][x_coord] = 0
        self.board[y_coord][x_coord - 1] = 0
        self.board[y_coord + 1][x_coord + 1] = 0
        self.board[y_coord - 1][x_coord - 1] = 0
        self.board[y_coord + 1][x_coord - 1] = 0
        self.board[y_coord - 1][x_coord + 1] = 0

    def set_cell_type1(self, x_coord, y_coord):
        self.board[y_coord + 1][x_coord] = -1
        self.board[y_coord + 1][x_coord + 1] = 0
        self.board[y_coord + 1][x_coord - 1] = 0
        self.board[y_coord + 2][x_coord] = 0
        self.board[y_coord][x_coord + 1] = 0
        self.board[y_coord - 1][x_coord] = 0
        self.board[y_coord][x_coord - 1] = 0
        self.board[y_coord + 2][x_coord + 1] = 0
        self.board[y_coord - 1][x_coord - 1] = 0
        self.board[y_coord + 2][x_coord - 1] = 0
        self.board[y_coord - 1][x_coord + 1] = 0

    def set_cell_type2(self, x_coord, y_coord):
        self.board[y_coord][x_coord + 1] = -1
        self.board[y_coord + 1][x_coord] = 0
        self.board[y_coord][x_coord + 2] = 0
        self.board[y_coord - 1][x_coord] = 0
        self.board[y_coord][x_coord - 1] = 0
        self.board[y_coord + 1][x_coord + 2] = 0
        self.board[y_coord - 1][x_coord - 1] = 0
        self.board[y_coord + 1][x_coord - 1] = 0
        self.board[y_coord - 1][x_coord + 2] = 0
        self.board[y_coord - 1][x_coord + 1] = 0
        self.board[y_coord + 1][x_coord + 1] = 0

    def get_board(self):
        return self.board

    def get_item(self, x, y):
        return self.board[x][y]

    def set_cell_colour_number(self,x,y,num):
        self.board[x][y] = num

    def initialize_board(self):
        self.board = [[0 for i in range(self.columns)] for j in range(self.rows)]
        n_walls = int(self.columns * self.rows * 0.3)
        for i in range(n_walls):
            cell_type = random.randint(0, 2)
            random_Y = random.randint(0, self.rows - 1)
            random_X = random.randint(0, self.columns - 1)
            if random_Y != 0 and random_X != 0 and random_Y != self.rows - 1 and random_X != self.columns - 1:
                self.board[random_Y][random_X] = -1
                if cell_type == 0:
                    self.set_cell_type0(random_X, random_Y)
                elif cell_type == 1 and random_Y < self.rows - 2:
                    self.set_cell_type1(random_X, random_Y)
                elif cell_type == 2 and random_X < self.columns - 2:
                    self.set_cell_type2(random_X, random_Y)
                else:
                    self.board[random_Y][random_X] = 0

    def print_board(self):
        print('\n'.join(' '.join('{0: ^3}'.format(str(i)) for i in row) for row in self.board))

    # Called by Server
    def change_tile(self,x, y, colour_index):
        target = self.get_item(x,y)
        if(target == 0):
            self.set_cell_colour_number(x,y,colour_index)
