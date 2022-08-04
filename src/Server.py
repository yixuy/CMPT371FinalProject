import sys
import socket
from _thread import *
import pickle
from GameLogic.Board import Board
import GameLogic.Util as Util
from NetworkUtils import *


server = IPADDRESS
port = PORTNUMBER

playerCount = 0
gameOn = False
gameStart = False
board = None

free_clients_indices = [0, 1, 2, 3]
clients = [None] * len(free_clients_indices)


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


def add_client_to_list(conn, addr, pCount):
    print("Server: using add_client_to_list()")
    # clients format: [ [conn, ip, port], [conn, ip, port], etc ],
    # clients indices are kept the same (even when removed)
    # if 0 < pCount < 5:
    #     if len(free_clients_indices) > 0:
    #         free_clients_indices.sort()  # so the smallest player number is preferred
    #         clients[free_clients_indices[0]] = [conn, addr[0], addr[1]]
    #     print("clients: ", clients)
    #     print("first client's port number: ", clients[0][2])
    #     playerNum = free_clients_indices[0] + 1  # bcs indices start from 0
    #     free_clients_indices.pop(0)
    #     return playerNum
    # return None

    # V2
    # print("clients: ", clients)
    # print("first client's port number: ", clients[0][2])
    if len(free_clients_indices) > 0:
        free_clients_indices.sort()  # so the smallest player number is preferred
        to_use_i = free_clients_indices.pop(0)
        print("to_use_i: ", to_use_i)
        print("break: ", clients[to_use_i])
        clients[to_use_i] = [conn, addr[0], addr[1]]
        playerNum = to_use_i + 1  # bcs indices start from 0
        return playerNum
    return None


def delete_client_from_list(conn, addr):
    try:
        for x in range(0, len(clients)):
            if clients[x][1] == addr[0] and clients[x][1] == addr[1]:
                clients[x] = None
                free_clients_indices.append(x)
    except:
        pass


def threaded_client(conn, addr, pCount, isGameInProgress):
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
                    print('Server generated board:')
                    reply = board

                elif data == GAME_PREPSTART:
                    print("Server: Preparing to start the game.")
                    # TODO: check if game can actually start,
                    #  it should broadcast to all clients at the same time
                    if pCount >= 2:
                        reply = GAME_START
                    else:
                        reply = 'Game requires minimum of 2 players.'

                elif data == GAME_PLAY:
                    # normal game info passing
                    pass

                elif data == PLAYER_JOIN:
                    print("data: new player has joined.")
                    pNum = add_client_to_list(conn, addr, 0)
                    # pNum = 2
                    reply = pNum
                    print("playerCount: ", pNum)


                    # Both of these checks will not allow player to join the game.
                    if isGameInProgress:
                        reply = GAME_IN_PROGRESS
                    # elif pCount > 4:
                    elif pNum is None:
                        reply = "GameFull"
                        print("-----------   Game is full")

                elif data == PLAYER_DISCONNECT:
                    # todo: remove them in clients, decrement player count
                    delete_client_from_list(conn, addr)

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
        # playerCount += 1
        gameOn = True  # When the first player 'starts' the game, other players just need to join (map generates once)


    start_new_thread(threaded_client, (conn, addr, playerCount, gameStart))  # playerCount can act as playerNumber
