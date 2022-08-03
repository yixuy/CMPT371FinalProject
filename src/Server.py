import pickle
import socket
from _thread import *

import GameLogic.util as util
from GameLogic.Board import Board

# global playerCount  # or change to rdy count

player_count = 0
game_on = False
start_game = False
server = "localhost"
port = 50000
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
            # print("data: ", data)
            if not data:
                break
            else:
                # reset the game
                if data == "reset":
                    print("data: 'reset' ")
                    # playerCount = 0
                    # pass
                # do the tile checking
                elif data == "get":
                    print("data: client getting info from server")
                    print("Server generated board:")
                    reply = board
                    # pass

                elif data == "playerOn":
                    print("data: new player has joined.")
                    reply = "newGameFromServer"
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
    # Server begins to start the game
    if start_game is True:
        if player_count < 2:
            start_game = False
            timer = TOTAL_GAME_TIME_IN_SECONDS
    else:  # Start game is false; reset the timer
        timer = TOTAL_GAME_TIME_IN_SECONDS

    """READY PHASE"""
    # game_on is True when at least one player is connected (initiated the map)
    if game_on is False:
        print("Starting new game...\nGenerating new map...")
        board = Board(util.TILEWIDTH, util.TILEHEIGHT)
        board.initialize_board()
        player_count += 1
        # When the first player 'starts' the game, other players just need to join (map generates once)
        game_on = True

    # If someone has already initiated a new game (map generated), just send players the map + required info.
    elif 1 <= player_count <= 4:
        player_count += 1

    p = player_count
    reply = str(p)
    conn.send(reply.encode())
    print("Connected to: ", addr)

    # playerCount can act as playerNumber
    start_new_thread(threaded_client, (conn, player_count))

    if player_count > 4:
        player_count -= 1
