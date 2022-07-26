from concurrent.futures import thread
import socket
from _thread import *
import pickle

global playerCount  # or change to rdy count

playerCount = 0
gameOn = False
gameStart = False
server = 'localhost'
port = 50000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
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


def threaded_client(conn, p, map):
    print("SERVER: In threaded_client thread")
    # conn.send(str.encode(str(p)))
    # conn.send(str(p).encode())
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
                    # pass
                # do the tile checking
                elif data == 'get':
                    print("data: client getting info from server")
                    reply = "dataFromServer"
                    # pass

                elif data == 'playerOn':
                    print("data: new player has joined.")
                    reply = "newGameFromServer"
                conn.sendall(reply.encode())

        except:
            break

    print("conn.close()")
    # idCount -= 1
    conn.close()

# while True:
#     conn, addr = s.accept()
#     p = 111
#     reply = str(p)
#     conn.send(reply.encode())
#     while True:
#         reply = ""
#         try:
#             data = conn.recv(4096).decode()
#             if data == "playerOn":
#                 print("data: new player has joined.")
#                 # playerCount += 1
#                 reply = "newGameFromServer"
#             conn.send(reply.encode())
#         except:
#             break
#             conn.close()


while True:
    conn, addr = s.accept()
    p = playerCount
    reply = str(p)
    conn.send(reply.encode())
    print("Connected to: ", addr)
    tileMap = 0  # placeholder for tile map

    '''START PHASE'''
    # Server begins to start the game
    if gameStart is True:
        pass

    '''READY PHASE'''
    # gameOn is True when at least one player is connected (initiated the map)
    if gameOn is False:
        print("Starting new game...\nGenerating new map...")
    #   TODO: Generate Map

        playerCount += 1
        gameOn = True  # When the first player 'starts' the game, other players just need to join (map generates once)

    # If someone has already initiated a new game (map generated), just send players the map + required info.
    elif 1 < playerCount < 4:
        playerCount += 1

    start_new_thread(threaded_client, (conn, playerCount, tileMap))  # playerCount can act as playerNumber