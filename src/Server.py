import sys
import socket
from _thread import *
import pickle
from GameLogic.Board import Board
import GameLogic.Util as Util
playerCount = 0
gameOn = False
gameStart = False
from GameLogic.Util import IPADDRESS, PORTNUMBER
board = None

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((IPADDRESS, PORTNUMBER))
except socket.error as e:
    str(e)

# queue up as many as 4 connect requests (the normal max) 
# before refusing outside connections.
s.listen(1)  # might need to increase (?)
print("Waiting for a connection, Server Started")

'''
Server:
    Receives new coords from Player1
    Checks new coords tile 
        If tile taken:
            Broadcast new coords to other players
        Else if tile not taken:
            Updates the Server tile to the Player1 colour (now tile is taken is taken by Player1)
            Broadcast Player1 new coords & coloured tile info to other players
'''


def threaded_client(conn, p):
    print("SERVER: In threaded_client thread")
    while True:
        reply = ""
        try:
            data = conn.recv(4096).decode()
            print(data)
            if not data:
                break
            else:
                # reset the game
                if data == "reset":
                    print("data: 'reset' ")
                
                # do the tile checking
                elif data == 'get':
                    print("data: client getting info from server")
                    print('Server generated board:')
                    reply = board

                elif data == 'playerOn':
                    print("data: new player has joined.")
                    reply = "newGameFromServer"
                    print("playerCount: ", playerCount)
                    if playerCount > 4:
                        reply = "GameFull"
                        print("-----------   Game is full")
                conn.sendall(pickle.dumps(reply))

        except:
            break

    print("conn.close()")
    conn.close()


while True:
    conn, addr = s.accept()

    '''START PHASE'''
    # Server begins to start the game
    if gameStart is True:
        if playerCount < 2:
            gameStart = False

    '''READY PHASE'''
    # gameOn is True when at least one player is connected (initiated the map)
    if gameOn is False:
        print("Starting new game...\nGenerating new map...")
        board = Board(Util.TILEWIDTH, Util.TILEHEIGHT)
        board.initialize_board()
        playerCount += 1
        gameOn = True  # When the first player 'starts' the game, other players just need to join (map generates once)

    # If someone has already initiated a new game (map generated), just send players the map + required info.
    elif 1 <= playerCount <= 4:
        playerCount += 1

    p = playerCount
    reply = str(p)
    conn.send(reply.encode())
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn, playerCount))  # playerCount can act as playerNumber

    if playerCount > 4:
        playerCount -= 1
