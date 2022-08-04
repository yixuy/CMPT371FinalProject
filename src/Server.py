import pickle
import socket
from _thread import *
import pickle
from GameLogic.Board import Board
import GameLogic.Util as Util
from NetworkUtils import *


server = IPADDRESS
port = PORTNUMBER

player_count = 0
players_ready = False
game_running = False
board = None
game_timer = 0
TOTAL_GAME_TIME_IN_SECONDS = 30


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

# queue up as many as 4 connect requests (the normal max)
# before refusing outside connections.
s.listen(1)  # might need to increase (?)
print("Waiting for a connection, Server Started")

"""
Server:
    Receives new coords from Player1
    Checks new coords tile 
        If tile taken:
            Broadcast new coords to other players
        Else if tile not taken:
            Updates the Server tile to the Player1 colour (now tile is taken is taken by Player1)
            Broadcast Player1 new coords & coloured tile info to other players
"""


def threaded_client(conn, p):
    print("SERVER: In threaded_client thread")

    while True:
        reply = ""
        try:
            data = conn.recv(4096).decode()
            if not data:
                break
            else:
                # reset the game
                if data == GAME_RESET:
                    print("data: 'reset' ")

                # do the tile checking
                elif data == GET_BOARD:
                    print("data: client getting info from server")
                    print("Server generated board:")
                    reply = board

                elif data == GAME_PREPSTART:
                    print("Server: Preparing to start the game.")
                    # TODO: check if game can actually start, it should broadcast to all clients at the same time
                    # reply = GAME_START
                    if player_count >= 2:
                        reply = GAME_START
                    else:
                        reply = "Game requires minimum of 2 players."

                elif data == GAME_PLAY:
                    # normal game info passing
                    pass

                elif data == PLAYER_JOIN:
                    print("data: new player has joined.")
                    reply = p
                    print("playerCount: ", player_count)
                    if player_count > 4:
                        reply = "GameFull"
                        print("-----------   Game is full")

                conn.sendall(pickle.dumps(reply))

        except:
            break

    print("conn.close()")
    conn.close()


while True:
    conn, addr = s.accept()

    """START PHASE"""
    # Server begins the game
    if game_running is True:
        if player_count < 2:
            game_running = False
            timer = TOTAL_GAME_TIME_IN_SECONDS
    else:  # Game is not running as the flag is false; reset the timer
        timer = TOTAL_GAME_TIME_IN_SECONDS

    """READY PHASE"""
    # player_ready is True when at least one player is connected (initiated the map)
    if players_ready is False:
        print("Starting new game...\nGenerating new map...")
        board = Board(Util.TILEWIDTH, Util.TILEHEIGHT)
        board.initialize_board()
        player_count += 1
        # When the first player 'starts' the game, other players just need to join (map generates once)
        players_ready = True

    # If someone has already initiated a new game (map generated), just send players the map + required info.
    elif 1 <= player_count <= 4:
        player_count += 1

    p = player_count
    reply = str(p)
    conn.send(reply.encode())
    print("Connected to: ", addr)

    # player_count can act as playerNumber
    start_new_thread(threaded_client, (conn, player_count))

    if player_count > 4:
        player_count -= 1
