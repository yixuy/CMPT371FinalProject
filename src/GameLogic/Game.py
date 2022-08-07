import pygame as pg
import sys
from .Player import *
from .Board import *
from .Tile import *
# Reference: https://www.youtube.com/watch?v=3UxnelT9aCo
class Game():
    def __init__(self, board_obj):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.board = board_obj.get_board()
        self.board_obj = board_obj
        self.grid = [[0 for i in range(TILEWIDTH)] for j in range(TILEHEIGHT)]
        pg.key.set_repeat(500, 100)

    def game_screen(self):
        self.all_sprites = pg.sprite.Group()
        # draw the wall
        for row in range(0, int(TILEWIDTH)):
            for col in range(0, int(TILEHEIGHT)):
                tile = None
                if (self.board[row][col] == -1):
                    tile = Tile(self, row, col, -1)
                else:
                    tile = Tile(self, row, col, 0)
                self.grid[row][col] = tile

        self.player = Player(self, 0, 0, 1)
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
        self.draw_grid()
        self.all_sprites.draw(self.screen)
        pg.display.flip()


    def update_tile(self, x, y, colour_index):
        tile = self.grid[x][y]
        tile.set_colour(colour_index)


    def input_dir(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                curr_x = self.player.get_x()
                curr_y = self.player.get_y()
                colour_index = self.player.get_colour_index()
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_LEFT:
                    if self.board[curr_x - 1][curr_y] != -1:
                        self.player.move(dx=-1)
                        self.board_obj.change_tile(curr_x,curr_y,colour_index)
                        self.update_tile(curr_x,curr_y,colour_index)
                if event.key == pg.K_RIGHT:
                    if curr_x + 1 < TILEWIDTH and self.board[curr_x + 1][curr_y] != -1:
                        self.player.move(dx=1)
                        self.board_obj.change_tile(curr_x,curr_y,colour_index)
                        self.update_tile(curr_x, curr_y, colour_index)
                if event.key == pg.K_UP:
                    if self.board[curr_x][curr_y - 1] != -1:
                        self.player.move(dy=-1)
                        self.board_obj.change_tile(curr_x,curr_y,colour_index)
                        self.update_tile(curr_x, curr_y, colour_index)
                if event.key == pg.K_DOWN:
                    if curr_y + 1 < TILEHEIGHT and self.board[curr_x][curr_y + 1] != -1:
                        self.player.move(dy=1)
                        self.board_obj.change_tile(curr_x,curr_y,colour_index)
                        self.update_tile(curr_x, curr_y, colour_index)

# board_test = Board(int(TILEWIDTH), int(TILEHEIGHT))
# board_test.initialize_board()
# g = Game(board_test)
#
# while True:
#     g.game_screen()
#     g.start_game()