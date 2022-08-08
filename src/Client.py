from GameLogic.Util import WIDTH, HEIGHT
import pygame

from Network import Network
from NetworkUtils import *
import sys

from GameLogic.Game import Game

pygame.font.init()

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Client")

"""Client's Game Implementation:
        - Onces client ready, waits for Server to signal that game is starting
        - Every 30fps, client will send Server its current coords
        - Server will process that coords and send client back the 'updated' tiles if 
            it passed the tile checking
        - If client passed the tile checking, client will update its own board (by setting the tile colour)
        """


def main(network, p):
    run = True
    clock = pygame.time.Clock()
    n = network
    player_num = p
    print("You are Player", player_num)
    # Game needs to be "ready" first, then be started
    is_game_ready = True
    is_game_starting = False
    is_game_running = False
    display_score = False
    g = None

    while run:
        clock.tick(60)  # Runs the game in 60fps
        try:
            '''READY PHASE (for client)
                - Player stays in READY PHASE until Server says it GAMESTART'''
            # Get data from the server in 60fps (to update own board)
            if is_game_ready is True:
                # Get the board once from the server
                board = n.send(GET_BOARD)

                # Generate the Game object with the game map
                if board:
                    g = Game(board.get_board())

                    win.fill((100, 100, 200))
                    font = pygame.font.SysFont("comicsans", 37)
                    text = font.render("Player is Ready!", True, (255, 0, 0))
                    text2 = font.render("Press Space to start game!", True, (255, 0, 0))
                    win.blit(text, (15, 150))
                    win.blit(text2, (15, 230))
                    pygame.display.flip()
                    is_game_ready = False
                    is_game_starting = True

            if is_game_starting is True:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            start_game = n.send(GAME_PREPSTART)
                            if start_game == GAME_START:
                                print("GAME CAN START...")
                                is_game_running = True
                                is_game_starting = False

            '''GAME PHASE (for client)'''
            # Actual Gameplay Logic
            if is_game_running is True:
                g.game_screen()
                update_counter = 0
                while True:
                    if update_counter % 60 == 0:
                        remaining_game_time = n.send(REMAINING_GAMETIME)
                        if remaining_game_time == REMAINING_TIME_MSG + "0s" or \
                                remaining_game_time == REMAINING_TIME_MSG + "-1s":  # Added as a safeguard
                            is_game_running = False
                            display_score = True
                            break
                    g.input_dir(network, player_num)
                    g.update()
                    g.draw()
                    update_counter += 1
            
            if display_score is True:
                # TODO: implement score displaying logic
                win.fill((100, 100, 200))
                font = pygame.font.SysFont("comicsans", 60)
                text = font.render("Game Over!", True, (255, 0, 0))
                win.blit(text, (100, 200))
                pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    msg = n.send(PLAYER_DISCONNECT)
                    pygame.quit()
                    sys.exit()

        except:
            run = False
            print("Couldn't get game")


def menu_screen():
    run = True
    clock = pygame.time.Clock()
    n = Network()

    win.fill((128, 128, 128))
    font = pygame.font.SysFont("comicsans", 50)
    text = font.render("Press Space to Play!", True, (255, 0, 0))
    win.blit(text, (20, 200))
    pygame.display.flip()

    while run:
        clock.tick(60)  # Makes the client game run in 60fps

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("button pressed - ready")
                    run = False
                    n.connect()
                    new_game = n.send(PLAYER_JOIN)
                    print("new game received: ", new_game)
                    if new_game == GAME_FULL or new_game == GAME_IN_PROGRESS:
                        print("Game is either full or in progress...\nClosing client connection...")
                        n.disconnect()
                        pygame.quit()
                    else:
                        n.set_player_num(new_game)
                        # UI
                        win.fill((200, 200, 128))
                        font = pygame.font.SysFont("comicsans", 45)
                        text = font.render("Player Getting Ready...", True, (255, 0, 0))
                        win.blit(text, (20, 200))
                        pygame.display.update()
            if event.type == pygame.QUIT:
                print("quitting game...")
                pygame.quit()
                run = False


    main(n, n.get_player_num())


while True:
    menu_screen()
