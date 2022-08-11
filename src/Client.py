import errno
from threading import Thread
from GameLogic.Board import Board
from GameLogic.Util import WIDTH, HEIGHT
import pygame
from Network import Network
from NetworkUtils import *
import sys
from GameLogic.Game import Game
import time

did_server_start_game = False
gameStartPrep = False
gameStart = False
gameRdy = True
g = None
did_player_rdy = False


pygame.font.init()

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Client")

'''Client's Game Implementation:
        - Onces client ready, waits for Server to signal that game is starting
        - Every 30fps, client will send Server its current coords
        - Server will process that coords and send client back the 'updated' tiles if
            it passed the tile checking
        - If client passed the tile checking, client will update its own board (by setting the tile colour)
        '''

def listen_for_messages(network, player_num):
    global did_server_start_game, gameStartPrep, gameStart, gameRdy, g, did_player_rdy
    print("Started listen_for_messages() Thread!")
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        try:
            print("gameRdy state:", gameRdy)
            print("gameStartPrep state:", gameStartPrep)

            if gameStartPrep:
                msg = network.recv()
                print('msg from server: %s' % msg)
                if msg["code"] == GAME_START:
                    did_server_start_game = True
                    # break
            if gameStart:
                msg = network.recv()
                print("gameStart")
                if msg["code"] == TESTING_PURPOSES+str(player_num):
                    print("TESTING received: %s" % msg)
                if msg["code"] == BOARD:
                # elif type(msg) is type(Board):
                    print("BOARD RECEIVED")
                    g.update_board(msg["data"])
                    print("CLIENT UPDATED THEIR BOARD")
            if gameRdy:
                msg = network.recv()
                print("gameRdy")
                # print("msg: ", msg)
                if msg["code"] == BOARD:
                    g.set_board(msg["data"])
                    print("BOARD: ", g.get_board())
                    # did_player_rdy = True
                    time.sleep(1)
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(e.errno))
                sys.exit()
            continue
        except Exception as e:
            print('Reading error: {}'.format(str(e)))
            sys.exit()
    print("Thread finished")


def main(network, p):
    global gameStartPrep, did_server_start_game, gameStart, gameRdy, g, did_player_rdy
    run = True
    clock = pygame.time.Clock()
    n = network
    player_num = p
    print("You are Player", player_num)

    # gameRdy = True
    # g = None

    t = Thread(target=listen_for_messages, args=(n, player_num))
    t.daemon = True
    t.start()

    while run:
        clock.tick(60)  # Runs the game in 60fps
        try:

            '''READY PHASE (for client)
                - Player stays in READY PHASE until Server says it GAMESTART'''
            # Get data from the server in 60fps (to update own board)
            if gameRdy is True:

                # Get the board once from the server
                if g is None:
                    g = Game()
                    n.send_only(GET_BOARD)
                    print('WE JUST HAVE SEND TO GET_BOARD')
                    print("----- ", g.get_board())
                # Generate the Game object with the game map
                # if did_player_rdy is True:
                print("IN MAIN: gameRdy state: ", gameRdy)
                if g.get_board() is not None:
                    print("BOARD IS READY")
                    gameRdy = False
                    gameStartPrep = True
                    print("WE HAVE SET GAMERDY TO FALSE: ", gameRdy)
                    win.fill((100, 100, 200))
                    font = pygame.font.SysFont("comicsans", 37)
                    text = font.render("Player is Ready!", True, (255, 0, 0))
                    text2 = font.render("Press Space to start game!", True, (255, 0, 0))
                    win.blit(text, (15, 150))
                    win.blit(text2, (15, 230))
                    pygame.display.flip()


            if gameStartPrep is True:
                # print("in gameStartPrep")
                if did_server_start_game:
                    gameStartPrep = False
                    gameStart = True
                else:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                n.send_only(GAME_PREPSTART)


            '''GAME PHASE (for client)'''
            # Actual Gameplay Logic
            if gameStart is True:
                print("Starting gameStart: " + str(gameStart))
                g.game_screen()
                while True:
                    n.send_only(GET_BOARD)
                    # g.update_board(updated_board_obj)
                    g.input_dir(network, player_num)
                    g.update()
                    g.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    msg = n.send(PLAYER_DISCONNECT)
                    pygame.quit()
                    sys.exit()

        except KeyboardInterrupt:
            pygame.quit()
            sys.exit()

        except Exception as e:
            print('Reading error: {}'.format(str(e)))
            print("Still continuing game loop as per normal.")
            continue

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
                    if new_game["code"] == GAME_FULL or new_game["code"] == GAME_IN_PROGRESS:
                        print("Game is either full or in progress...\nClosing client connection...")
                        n.disconnect()
                        pygame.quit()
                    else:
                        n.set_player_num(new_game["data"])
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

