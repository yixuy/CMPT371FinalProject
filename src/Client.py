import errno
import sys
import time
from threading import Thread

import pygame

from GameLogic.Game import Game
from GameLogic.Util import WIDTH, HEIGHT, GAME_STARTING_TIME, COLOURS
from Network import Network
from NetworkUtils import *

did_server_start_game = False
is_game_ready = True
is_game_starting = False
is_game_running = False
is_game_over = False

scores = None
game_end = False
g = None

pygame.font.init()

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Client")
font = pygame.font.SysFont("comicsans", 37)

'''Client's Game Implementation:
        - Onces client ready, waits for Server to signal that game is starting
        - Every 30fps, client will send Server its current coords
        - Server will process that coords and send client back the 'updated' tiles if
            it passed the tile checking
        - If client passed the tile checking, client will update its own board (by setting the tile colour)
        '''


# NOTE: I'm leaving the print statements here for now because this threading is not fully reliable yet!
def listen_for_messages(network, player_num):
    global did_server_start_game, is_game_starting, is_game_running, is_game_ready, g, is_game_over, scores, game_end
    print("[Player %s] - Started listen_for_messages() Thread!" % player_num)
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        # print("[THREAD]: gameRdy = %s, gameStartPrep = %s, gameStart = %s" % (gameRdy, gameStartPrep, gameStart))
        try:
            if game_end:
                msg = network.recv()
                print("IN GAME END", msg)
                if msg["code"] is not None:
                    if msg["code"] == DISPLAY_SCORE and msg["data"] is not None:
                        scores = msg["data"]
                        print("DISPLAY SCORE")
                        break

            elif is_game_running:
                print("[THREAD]: In gameStart")
                msg = network.recv()

                print("THREAD [gameStart]: gameStart, msg from server: %s" % msg)

                if msg is not None:
                    if msg["code"] == GAME_OVER and msg["data"] is not None:
                        print("CLIENT GAMEOVER")
                        print(msg["data"].print_board())
                        g.update_board(msg["data"])
                        time.sleep(1)
                        is_game_over = True

                    elif msg["code"] == BOARD and msg["data"] is not None:
                        g.update_board(msg["data"])


            elif is_game_starting:
                print("[THREAD]: In gameStartPrep")
                msg = network.recv()
                if msg is None:
                    continue
                print('THREAD [gameStartPrep]: msg from server: %s' % msg)
                msg_code = msg["code"]
                if msg_code is not None and msg_code == GAME_START:
                    g.update_board(msg["data"])
                    did_server_start_game = True
                    # time.sleep(1)     # Seems to work now without this (Re-enable this if thread does not go to gameStart properly)
                elif msg_code == GAME_NOT_ENOUGH_PLAYERS:
                    print("[gameStartPrep] - Game can't start because not enough players ready.")

            elif is_game_ready:
                print("THREAD [gameRdy]: gameRdy")
                msg = network.recv()
                if msg["code"] is not None and msg["code"] == BOARD:
                    g.set_board(msg["data"])
                    print("THREAD: BOARD: ", g.get_board())

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(e.errno))
                sys.exit()
            if e.errno == errno.EPIPE:  # Broken pipe (either from server offline, etc)
                print('Reading error: {}'.format(e.errno))
                close_game(network)
            continue

        except Exception as e:
            print('Reading error: {}'.format(str(e)))
            pygame.quit()
            sys.exit()
    print("Thread finished")


def close_game(network):
    print("Closing game...")
    reply = {"code": PLAYER_DISCONNECT}
    network.send_only(reply)
    network.disconnect()
    pygame.quit()
    sys.exit()


def game_start_count_down(network):
    count_down = GAME_STARTING_TIME
    time_delay = 1000
    timer_event = pygame.USEREVENT + 1
    pygame.time.set_timer(timer_event, time_delay)
    while count_down > 0:
        for event in pygame.event.get():
            if event.type == timer_event:
                count_down -= 1
        win.fill(COLOURS[0])
        text = font.render("GAME STARTING IN:", True, (255, 0, 0))
        text2 = font.render(str(count_down), True, (255, 0, 0))
        win.blit(text, text.get_rect(center=(WIDTH / 2, (HEIGHT / 2) - 10)))
        win.blit(text2, text2.get_rect(center=(WIDTH / 2, (HEIGHT / 2) + 40)))
        pygame.display.flip()
    else:
        reply = {"code": START_SERVER_TIMER}
        network.send_only(reply)


def main(network, p):
    global is_game_starting, did_server_start_game, is_game_running, is_game_ready, g, is_game_over, scores, game_end
    run = True
    clock = pygame.time.Clock()
    n = network
    player_num = p
    print("You are Player", player_num)

    t = Thread(target=listen_for_messages, args=(n, player_num))
    t.daemon = True
    t.start()

    while run:
        reply = {}
        clock.tick(60)  # Runs the game in 60fps
        try:
            '''READY PHASE (for client)
                - Player stays in READY PHASE until Server says it GAMESTART'''
            # Get data from the server in 60fps (to update own board)
            if is_game_ready is True:
                # Get the board once from the server
                if g is None:
                    g = Game()
                    g.set_player_num(player_num)
                    reply["code"] = GET_BOARD
                    n.send_only(reply)

                # Generate the Game object with the game map
                else:
                    is_game_starting = True
                    is_game_ready = False

                    win.fill((100, 100, 200))
                    text = font.render("Player is Ready!", True, (255, 0, 0))
                    text2 = font.render("Press Space to start game!", True, (255, 0, 0))
                    win.blit(text, (15, 150))
                    win.blit(text2, (15, 230))
                    pygame.display.flip()

            if is_game_starting is True:
                if did_server_start_game:
                    is_game_running = True
                    is_game_starting = False

                else:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                reply["code"] = GAME_PREPSTART
                                n.send_only(reply)
                            if event.type == pygame.K_ESCAPE:
                                close_game(n)
                        if event.type == pygame.QUIT:
                            close_game(n)

            '''GAME PHASE (for client)'''
            # Actual Gameplay Logic
            if is_game_running is True:
                print("Starting gameStart: " + str(is_game_running))
                # ** Wait time till game starts for all players ( Uncomment when ready to use )
                game_start_count_down(n)
                g.game_screen()

                while not is_game_over:
                    g.input_dir(network, player_num)
                    g.update()
                    g.draw()

                is_game_running = False
                game_end = True
                n.send_only("Game is over")

                while scores is None:
                    continue

                colours_dict = {1: "Red", 2: "Blue", 3: "Green", 4: "Yellow"}
                display_score = "Game Over!"
                for player, score in scores.items():
                    display_score += colours_dict[player] + ": " + str(score) + ", "

                win.fill((100, 100, 200))
                text = font.render(display_score, True, (255, 0, 0))
                win.blit(text, (15, 150))
                pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        close_game(n)

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
                        close_game(n)
                    else:
                        n.set_player_num(new_game["data"])
                        # UI
                        win.fill((200, 200, 128))
                        font = pygame.font.SysFont("comicsans", 45)
                        text = font.render("Player Getting Ready...", True, (255, 0, 0))
                        win.blit(text, (20, 200))
                        pygame.display.update()
            if event.type == pygame.QUIT:
                close_game(n)

    main(n, n.get_player_num())


while True:
    menu_screen()
