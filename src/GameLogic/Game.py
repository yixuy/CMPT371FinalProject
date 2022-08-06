import sys

from .Board import *
from .Player import *
from .Wall import *


# Reference: https://www.youtube.com/watch?v=3UxnelT9aCo
class Game:
    def __init__(self, board):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.board = board
        pg.key.set_repeat(500, 100)

    def game_screen(self):
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.player = Player(self, 0, 0, COLOURS[1])

        # draw the wall
        for row in range(0, int(TILEWIDTH)):
            for col in range(0, int(TILEHEIGHT)):
                if self.board[row][col] == -1:
                    Wall(self, row, col)

    def start_game(self):
        while True:
            self.dt = self.clock.tick(FPS) / 1000
            self.input_dir()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        self.all_sprites.update()

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        self.screen.fill(COLOURS[0])
        self.draw_grid()
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def input_dir(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                curr_x = self.player.get_x()
                curr_y = self.player.get_y()
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_LEFT:
                    if self.board[curr_x - 1][curr_y] != -1:
                        self.player.move(dx=-1)
                if event.key == pg.K_RIGHT:
                    if curr_x + 1 < TILEWIDTH and self.board[curr_x + 1][curr_y] != -1:
                        self.player.move(dx=1)
                if event.key == pg.K_UP:
                    if self.board[curr_x][curr_y - 1] != -1:
                        self.player.move(dy=-1)
                if event.key == pg.K_DOWN:
                    if curr_y + 1 < TILEHEIGHT and self.board[curr_x][curr_y + 1] != -1:
                        self.player.move(dy=1)


board = Board(int(TILEWIDTH), int(TILEHEIGHT))
board.initialize_board()
board = board.get_board()
print(board)
# g = Game(board)

# while True:
#     g.game_screen()
#     g.start_game()
