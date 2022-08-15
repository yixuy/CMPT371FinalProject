import errno
import sys
from threading import Thread

import pygame

from GameLogic.Game import Game
from GameLogic.Util import WIDTH, HEIGHT, GAME_STARTING_TIME, COLOURS
from Network import Network
from NetworkUtils import *

# Global flags to control the state of the game
did_server_start_game = False
game_start_prep = False
game_start = False
game_rdy = True
is_game_over = False
scores = None
game_end = False
g = None

pygame.font.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Client")
font = pygame.font.SysFont("comicsans", 37)

'''
Client's Game Implementation:
    - Once client is ready, wait for Server to signal that game is starting
    - Every 60fps, client will send Server its current coords and colour
    - Server will process that coords and send client back the 'updated' tiles if it passed the tile checking
    - If client passed the tile checking, client will update its own board (by setting the tile colour)
'''


# Thread for client to listen to Server requests continuously
def listen_for_messages(network, player_num):
    global did_server_start_game, game_start_prep, game_start, game_rdy, g, is_game_over, scores, game_end
    print("[Player %s] - Started listen_for_messages() Thread!" % player_num)
    clock = pygame.time.Clock()
    while True:
        # This runs the game at 60fps
        clock.tick(60)

        # Depending on the state of the game, client will receive different messages from Server
        try:

            # State: Game End
            # Client will receive the final scores from the Server
            if game_end:
                msg = network.recv()
                if len(msg) > 0 and msg["code"] is not None:
                    if msg["code"] == DISPLAY_SCORE and msg["data"] is not None:
                        scores = msg["data"]
                        break

            # State: Game Start
            # Client will receive data during game play
            elif game_start:
                msg = network.recv()
                if msg is not None and len(msg) > 0:

                    # If the game has ended, Client updates the board one final time and changes their game state to game_end
                    if msg["code"] == GAME_OVER and msg["data"] is not None:
                        g.update_board(msg["data"])
                        is_game_over = True

                    # If the game has not ended, Client will receive updated boards from the Server
                    elif msg["code"] == BOARD and msg["data"] is not None:
                        g.update_board(msg["data"])

            # State: Game Start Prep
            # Client will receive signal to start the game
            elif game_start_prep:
                msg = network.recv()
                if msg is None:
                    continue
                msg_code = msg["code"]

                # Client receives the signal from Server to start the game
                if msg_code is not None and msg_code == GAME_START:
                    g.update_board(msg["data"])
                    did_server_start_game = True

                # Client is not allowed to start game because at least 2 players are not ready
                elif msg_code == GAME_NOT_ENOUGH_PLAYERS:
                    print("Game can't start because not enough players ready.")

            # State: Game Ready
            # Client has joined game successfully and will receive the game board
            elif game_rdy:
                msg = network.recv()
                if msg["code"] is not None and msg["code"] == BOARD:
                    g.set_board(msg["data"])

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
    reply = {"code": PLAYER_DISCONNECT}
    network.send_only(reply)
    network.disconnect()
    pygame.quit()
    sys.exit()


def game_start_count_down():
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


# Main is where the game for client runs
def main(network, p):
    global game_start_prep, did_server_start_game, game_start, game_rdy, g, is_game_over, scores, game_end
    run = True
    clock = pygame.time.Clock()
    n = network
    player_num = p

    # Create thread for Client to continuously listen to requests from the Server
    # This is to create a full duplex connection so that the Server and the Client can send and receive continuously (i.e. non-blocking)
    # Setting a "full duplex" connection aims to make sure Clients move game states concurrently
    t = Thread(target=listen_for_messages, args=(n, player_num))
    t.daemon = True
    t.start()

    while run:
        reply = {}
        clock.tick(60)  # Runs the game in 60fps
        try:
            '''READY PHASE (for client)
                - Player stays in READY PHASE until Server signals game_start'''
            # Get data from the server in 60fps (to update own board)
            if game_rdy is True:
                # Get the board initially from the server
                if g is None:
                    g = Game()
                    g.set_player_num(player_num)
                    reply["code"] = GET_BOARD
                    n.send_only(reply)

                # Generate the Game object with the game map
                else:
                    # Move to the next game state: Game Start Prep
                    game_start_prep = True
                    game_rdy = False

                    # UI changes when Player has joined Game
                    win.fill((100, 100, 100))
                    colours_dict = {1: "Red", 2: "Blue", 3: "Green", 4: "Yellow"}
                    text = font.render("Player is Ready!", True, (255, 255, 255))
                    text2 = font.render("Press Space to start game!", True, (255, 255, 255))
                    text3 = font.render("Your colour is: " + colours_dict[player_num], True, COLOURS[player_num])
                    win.blit(text, (15, 150))
                    win.blit(text2, (15, 230))
                    win.blit(text3, (15,280))
                    pygame.display.flip()

            if game_start_prep is True:
                if did_server_start_game:
                    # Move to next game state: Game Start
                    game_start_prep = False
                    game_start = True

                else:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                # Client lets Server know they are ready to start game
                                reply["code"] = GAME_PREPSTART
                                n.send_only(reply)
                            if event.type == pygame.K_ESCAPE:
                                close_game(n)
                        if event.type == pygame.QUIT:
                            close_game(n)

            '''GAME PHASE (for client)'''
            # Actual Gameplay Logic
            if game_start is True:
                game_start_count_down()
                g.game_screen()

                # While game is not over:
                # Get player direction and send to Server to handle board updates
                # Client receives the updated board from the Server
                # Client will update their board and handle UI changes
                while is_game_over is False:
                    g.input_dir(network, player_num)
                    g.update()
                    g.draw()

                # Move to next game state: Game End
                game_start = False
                game_end = True

                # This is a redundant request sent to Server in case Server is blocked in a receiving call
                n.send_only("Game is over")

                # Wait until final scores from the Server have been received
                while scores is None:
                    continue

                # UI setup to display final scores
                colours_dict = {1: "Red", 2: "Blue", 3: "Green", 4: "Yellow"}
                game_over_text = "Game Over!"
                win.fill((100, 100, 100))
                text = font.render(game_over_text, True, (255, 255, 255))
                win.blit(text, (15, 150))
                pixel_height = 200
                for player, score in scores.items():
                    display_score = colours_dict[player] + ": " + str(score)
                    score_text = font.render(display_score, True, COLOURS[player])
                    win.blit(score_text, (15, pixel_height))
                    pixel_height += 50
                exit_text = font.render("Press Space to exit", True, (255, 255, 255))
                win.blit(exit_text, (15, pixel_height + 30))
                text1 = font.render("Your colour is: " + colours_dict[player_num], True, COLOURS[player_num])
                win.blit(text1, (15, pixel_height+50))
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
            continue


def menu_screen():
    run = True
    clock = pygame.time.Clock()

    # Opens Client socket
    # Network class handles all socket programming from the Client
    n = Network()

    # Menu screen UI
    win.fill((128, 128, 128))
    font = pygame.font.SysFont("comicsans", 50)
    text = font.render("Press Space to Play!", True, (255, 255, 255))
    win.blit(text, (20, 200))
    pygame.display.flip()

    while run:
        clock.tick(60)  # Makes the client game run in 60fps
        reply = {}

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    run = False

                    # Client socket connects with Server
                    n.connect()

                    reply["code"] = PLAYER_JOIN

                    # Send is a blocking call, and waits for Server to return message
                    new_game = n.send(reply)
                    new_game_code = new_game["code"]

                    if new_game_code == GAME_FULL or new_game_code == GAME_IN_PROGRESS:
                        print("Game is either full or in progress...\nClosing client connection...")
                        close_game(n)
                    else:
                        n.set_player_num(new_game["data"])

                        # UI changes when Player is ready to play game
                        win.fill((200, 200, 128))
                        font = pygame.font.SysFont("comicsans", 45)
                        text = font.render("Player Getting Ready...", True, (255, 0, 0))
                        win.blit(text, (20, 200))
                        pygame.display.update()

            if event.type == pygame.QUIT:
                close_game(n)

    # Game is run for specific client with their assigned player number
    main(n, n.get_player_num())


while True:
    menu_screen()
