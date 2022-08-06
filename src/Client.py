from GameLogic.Util import WIDTH, HEIGHT
import pygame

from Network import Network
from NetworkUtils import *
# gameRdy = False
# gameStart = False

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
    gameRdy = True
    gameStart = False
    gameStartPrep = False
    g = None

    while run:
        clock.tick(60)  # Runs the game in 60fps
        try:
            '''READY PHASE (for client)
                - Player stays in READY PHASE until Server says it GAMESTART'''
            # Get data from the server in 60fps (to update own board)
            if gameRdy is True:
                # Get the board once from the server
                board = n.send(GET_BOARD)

                # Generate the Game object with the game map
                if board:
                    g = Game(board.get_board())

                    win.fill((100, 100, 200))
                    font = pygame.font.SysFont("comicsans", 60)
                    text = font.render("Player is Ready!\nPress to Start", True, (255, 0, 0))
                    win.blit(text, (100, 200))
                    pygame.display.flip()
                    gameRdy = False
                    gameStartPrep = True

            if gameStartPrep is True:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        isGameStart = n.send(GAME_PREPSTART)
                        if isGameStart == GAME_START:
                            print("GAME CAN START...")
                            g.game_screen()
                            g.start_game()
                            gameStart = True
                            gameStartPrep = False

            '''START PHASE (for client)'''
            # Actual Gameplay Logic
            if gameStart is True:
                # play the game like normal
                game = n.send(GAME_PLAY)

        except:
            run = False
            print("Couldn't get game")
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                msg = n.send(PLAYER_DISCONNECT)
                pygame.quit()

        # run = False


def menu_screen():
    run = True
    clock = pygame.time.Clock()
    n = Network()

    win.fill((128, 128, 128))
    font = pygame.font.SysFont("comicsans", 60)
    text = font.render("Click to Play!", True, (255, 0, 0))
    win.blit(text, (100, 200))
    pygame.display.update()

    while run:
        clock.tick(60)  # Makes the client game run in 60fps

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("quitting game...")
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("button pressed - ready")
                run = False
                n.connect()
                new_game = n.send(PLAYER_JOIN)
                print("new game received: ", new_game)
                if new_game == GAME_FULL or new_game == GAME_IN_PROGRESS:
                    print("Game is either full or in progress...\nClosing client connection...")
                    n.disconnect()
                    pygame.quit()
                    run = False
                else:
                    n.set_player_num(new_game)

                # UI
                win.fill((200, 200, 128))
                font = pygame.font.SysFont("comicsans", 60)
                text = font.render("Player Getting Ready...", True, (255, 0, 0))
                win.blit(text, (100, 200))
                pygame.display.update()

    main(n, n.get_player_num())


while True:
    menu_screen()
