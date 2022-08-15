import pygame
from NetworkUtils import CLIENT_GAME_TIME_IN_SECONDS, GAME_PLAY, PLAYER_DISCONNECT
import pygame as pg
import sys
from .Player import *
from .Board import *
from .Tile import *
from .Util import *
# Reference: https://www.youtube.com/watch?v=3UxnelT9aCo

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT + 80))
        self.bottom_screen_rect_obj = pg.draw.rect(self.screen, (0, 200, 0), (0, HEIGHT, WIDTH, 80))  # Only for timer UI rn
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.board = None
        self.board_obj = None
        self.grid = [[0 for i in range(TILEWIDTH)] for j in range(TILEHEIGHT)]
        self.player = None
        self.player_num = 0
        pg.key.set_repeat(500, 100)

        # Might be temporary - allows each client to run their own timer (for clock UI testing purposes)
        self.time_delay = 1000
        self.timer = CLIENT_GAME_TIME_IN_SECONDS
        self.timer_event = pygame.USEREVENT + 1
        pg.time.set_timer(self.timer_event, self.time_delay)
        self.font = pygame.font.SysFont("Consolas", 37)


    def setup_grid(self):
        self.all_sprites = pg.sprite.Group()
        for row in range(0, int(TILEWIDTH)):
            for col in range(0, int(TILEHEIGHT)):
                tile = None
                if (self.board[row][col] == -1):
                    tile = Tile(self, row, col, -1)
                else:
                    tile = Tile(self, row, col, 0)
                self.grid[row][col] = tile

    def set_player_num(self, player_num):
        self.player_num = player_num

    def game_screen(self):
        if (self.player_num == 1):
            self.player = Player(self, 0, 0, self.player_num)
        if (self.player_num == 2):
            self.player = Player(self, TILEWIDTH-1, 0, self.player_num)
        if (self.player_num == 3):
            self.player = Player(self, 0, TILEHEIGHT-1, self.player_num)
        if (self.player_num == 4):
            self.player = Player(self, TILEWIDTH-1, TILEHEIGHT-1, self.player_num)

    def start_game(self):
        while True:
            self.dt = self.clock.tick(FPS) / 10
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
        self.update_timer()
        self.draw_grid()
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def update_timer(self):
        clock_text = self.font.render(str(self.timer), True, (255, 255, 255))
        text_rect = clock_text.get_rect(center=self.bottom_screen_rect_obj.center)
        self.bottom_screen_rect_obj = pg.draw.rect(self.screen, (100, 100, 100), (0, HEIGHT, WIDTH, 80))  # Redraws the rect (to clear out previous timer text)
        self.screen.blit(clock_text, text_rect)

    def update_tile(self, x, y, colour_index):
        tile = self.grid[x][y]
        tile.set_colour(colour_index)

    def set_board(self, new_board_obj):
        self.board_obj = new_board_obj
        self.board = new_board_obj.get_board()
        self.setup_grid()

    def update_board(self, updated_board_obj):
        self.board_obj = updated_board_obj
        self.board = updated_board_obj.get_board()
        for row in range(TILEHEIGHT):
            for col in range(TILEHEIGHT):
                self.update_tile(row, col, self.board[row][col])
        # self.update_tile(10, 10, self.board[10][10])

    def get_board(self):
        return self.board

    def input_dir(self, network, player):

        msg = {
                "code": GAME_PLAY,
                "player": str(player),
                "x": self.player.get_x(),
                "y": self.player.get_y()
               }
        for event in pg.event.get():
            if event.type == self.timer_event:
                if self.timer == 0:
                    network.send_only({"code": "Game is Over!"})
                else:
                    self.timer -= 1

            if event.type == pg.QUIT:
                network.send_only({"code": PLAYER_DISCONNECT})
                self.quit()
            if event.type == pg.KEYDOWN:
                curr_x = self.player.get_x()
                curr_y = self.player.get_y()
                colour_index = self.player.get_colour_index()

                if event.key == pg.K_ESCAPE:
                    network.send_only({"code": PLAYER_DISCONNECT})
                    self.quit()
                elif event.key == pg.K_LEFT:
                    if curr_x >= 1 and self.board[curr_x - 1][curr_y] != -1:
                        self.player.move(dx=-1)
                        msg["move"] = LEFT
                        network.send_only(msg)
                        return
                elif event.key == pg.K_RIGHT:
                    if curr_x + 1 < TILEWIDTH and self.board[curr_x + 1][curr_y] != -1:
                        self.player.move(dx=1)
                        msg["move"] = RIGHT
                        network.send_only(msg)
                        return
                elif event.key == pg.K_UP:
                    if curr_y >= 1 and self.board[curr_x][curr_y - 1] != -1:
                        self.player.move(dy=-1)
                        msg["move"] = UP
                        network.send_only(msg)
                elif event.key == pg.K_DOWN:
                    if curr_y + 1 < TILEHEIGHT and self.board[curr_x][curr_y + 1] != -1:
                        self.player.move(dy=1)
                        msg["move"] = DOWN
                        network.send_only(msg)
                        return