import random
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

    # Cell Type 0: 1x1 cell
    # Cell Type 1: 1x2 cell
    # Cell Type 2: 2x1 cell
    def setCell(self, x_coord, y_coord):
        self.board[y_coord+1][x_coord] = 0
        self.board[y_coord][x_coord+1] = 0
        self.board[y_coord-1][x_coord] = 0
        self.board[y_coord][x_coord-1] = 0
        self.board[y_coord+1][x_coord+1] = 0
        self.board[y_coord-1][x_coord-1] = 0
        self.board[y_coord+1][x_coord-1] = 0
        self.board[y_coord-1][x_coord+1] = 0

    def initializeBoard(self):
        self.board = [[0 for i in range(self.height)] for j in range(self.width)]
        n_walls = int(self.height * self.width * 0.2)
        for i in range(n_walls):
            # cellType = random.randint(0,2)
            random_Y = random.randint(0, self.width-1)
            random_X = random.randint(0, self.height-1)
            self.board[random_Y][random_X] = -1
            if (random_Y//2 != 0):
                if(random_Y != 0 and random_X != 0 and random_Y != self.height-1 and random_X != self.width-1):
                    self.setCell(random_X, random_Y)

    def printBoard(self):
        print("TEST")
        print('\n'.join(' '.join('{0: ^3}'.format(str(i)) for i in row) for row in self.board))


newBoard = Board(10,10)
newBoard.initializeBoard()
newBoard.printBoard()