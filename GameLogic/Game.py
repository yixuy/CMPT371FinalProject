import pygame as pg
import sys
# from settings import *
from Wall import *
from Player import *
from util import *
from Board import * 
# Reference: https://www.youtube.com/watch?v=3UxnelT9aCo

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        
    def game_screen(self):
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.player = Player(self, 0, 0, COLOURS[1])
        # self.player_2 = Player(self, 31, 0, COLOURS[2] )
        # self.player_3 = Player(self, 31, 31, COLOURS[3] )
        # self.player_4 = Player(self, 0, 31, COLOURS[4] )
        
        board = Board(32, 32)
        board.initializeBoard()
        board = board.getBoard()
        print(board)
        for row in range(0,32):
            for col in range(0,32):
                if(board[row][col] == -1):
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
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_LEFT:
                    self.player.move(dx=-1)
                if event.key == pg.K_RIGHT:
                    self.player.move(dx=1)
                if event.key == pg.K_UP:
                    self.player.move(dy=-1)
                if event.key == pg.K_DOWN:
                    self.player.move(dy=1)
    # def show_start_screen():


# create the game object
g = Game()
# g.show_start_screen()
while True:
    g.game_screen()
    g.start_game()
    g.show_go_screen()
    
    
        
# board = Board(32, 32)
# board.initializeBoard()
# board.printBoard()