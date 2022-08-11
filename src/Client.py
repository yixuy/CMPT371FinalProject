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
            # print("THREAD: gameRdy state:", gameRdy)
            # print("THREAD: gameStartPrep state:", gameStartPrep)

            if gameStartPrep:
                msg = network.recv()
                print('THREAD [gameStartPrep]: msg from server: %s' % msg)
                msg_code = msg["code"]
                if msg_code == GAME_START:
                    did_server_start_game = True
                elif msg_code == GAME_NOT_ENOUGH_PLAYERS:
                    print("[gameStartPrep] - Game can't start because not enough players ready.")
                    # break
            if gameStart:
                msg = network.recv()
                print("THREAD [gameStart]: gameStart, msg from server: %s" % msg)
                if msg is not None and len(msg) > 0 and msg["code"] == BOARD:
                    if type(msg["data"]) == Board:
                        print("THREAD: BOARD RECEIVED")
                        g.update_board(msg["data"])
                        print("THREAD: CLIENT UPDATED THEIR BOARD")
            if gameRdy:
                msg = network.recv()
                print("THREAD [gameRdy]: gameRdy")
                # print("msg: ", msg)
                if msg["code"] == BOARD:
                    g.set_board(msg["data"])
                    print("THREAD: BOARD: ", g.get_board())
                    # did_player_rdy = True
                    time.sleep(1)

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('THREAD [IOError]: Reading error: {}'.format(e.errno))
                sys.exit()
            continue

        except Exception as e:
            print('THREAD [Exception]: Reading error: {}'.format(str(e)))
            sys.exit()
    print("Thread finished")


def main(network, p):
    global gameStartPrep, did_server_start_game, gameStart, gameRdy, g, did_player_rdy
    run = True
    clock = pygame.time.Clock()
    n = network
    player_num = p
    print("You are Player", player_num)

    t = Thread(target=listen_for_messages, args=(n, player_num))
    t.daemon = True
    t.start()

    while run:
        clock.tick(60)  # Runs the game in 60fps
        reply = {}

        try:
            '''READY PHASE (for client)
                - Player stays in READY PHASE until Server says it GAMESTART'''
            # Get data from the server in 60fps (to update own board)
            if gameRdy is True:

                # Get the board once from the server
                if g is None:
                    g = Game()
                    reply["code"] = GET_BOARD
                    n.send_only(reply)
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
                                reply["code"] = GAME_PREPSTART
                                n.send_only(reply)
                        if event.type == pygame.QUIT:
                            print("Player wants to quit...")
                            run = False
                            reply["code"] = PLAYER_DISCONNECT
                            n.send_only(reply)
                            pygame.quit()
                            sys.exit()


            '''GAME PHASE (for client)'''
            # Actual Gameplay Logic
            if gameStart is True:
                print("Starting gameStart: " + str(gameStart))
                g.game_screen()

                while True:
                    reply["code"] = GET_BOARD
                    # n.send_only(reply)      # *This is causing the server to keep receiving empty message once ctrl+c
                    # g.update_board(updated_board_obj)
                    g.input_dir(network, player_num)
                    g.update()
                    g.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Player wants to quit...")
                    run = False
                    reply["code"] = PLAYER_DISCONNECT
                    n.send_only(reply)
                    n.disconnect()
                    pygame.quit()
                    sys.exit()

        # breaks the server side -> makes the message recieved in server to be empty,thus break
        except KeyboardInterrupt:
            print("Keyboard interrupt: Closing game...")
            n.send_only({"code": PLAYER_DISCONNECT})
            n.disconnect()
            pygame.quit()
            sys.exit()

        except Exception as e:
            print('Reading error [MAIN]: {}'.format(str(e)))
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
        reply = {}
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("button pressed - ready")
                    run = False
                    n.connect()
                    reply["code"] = PLAYER_JOIN
                    new_game = n.send(reply)
                    print("new game received: ", new_game)
                    new_game_code = new_game["code"]
                    if new_game_code == GAME_FULL or new_game_code == GAME_IN_PROGRESS:
                        print("Game is either full or in progress...\nClosing client connection...")
                        n.disconnect()
                        pygame.quit()
                        sys.exit()
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
                run = False
                n.send_only({"code": PLAYER_DISCONNECT})
                n.disconnect()
                pygame.quit()
                sys.exit()

    main(n, n.get_player_num())

while True:
    menu_screen()

