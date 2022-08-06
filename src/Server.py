import sys
import socket
from _thread import *
import pickle
from GameLogic.Board import Board
import GameLogic.Util as Util
from NetworkUtils import *


server = IPADDRESS
port = PORTNUMBER

MAX_PLAYERS = 4
playerCount = 0
gameOn = False
gameStart = False
board = None

free_clients_indices = [0, 1, 2, 3]
clients = [None] * len(free_clients_indices)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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


def add_client_to_list(p_conn, p_addr):
    print("Server: using add_client_to_list()")
    # clients format: [ [conn, ip, port], [conn, ip, port], etc ],
    # Note: clients indices are kept the same (even when removed)

    # This is to check if client is already connected (to counter the potential bugs on client side)
    conn_item_list = [[p_conn, p_addr[0], p_addr[1]]]
    check = any(True for i in clients if i in conn_item_list)
    if check:
        return -1

    if len(free_clients_indices) > 0:
        free_clients_indices.sort()  # so the smallest player number is preferred
        to_use_i = free_clients_indices.pop(0)
        clients[to_use_i] = [p_conn, p_addr[0], p_addr[1]]
        player_num = to_use_i + 1  # bcs indices start from 0
        return player_num
    return None


def delete_client_from_list(p_conn, addr):
    try:
        for x in range(0, len(clients)):
            if clients[x][1] == addr[0] and clients[x][1] == addr[1]:
                clients[x] = None
                free_clients_indices.append(x)
    except:
        pass


def broadcast(msg):
    for client in clients:
        if client is not None:
            my_conn = client[0]
            my_conn.send(pickle.dumps(msg))


def threaded_client(p_conn, p_addr):
    print("SERVER: In threaded_client thread")
    player_num = 0
    while True:
        p_count = MAX_PLAYERS - len(free_clients_indices)
        print(" ----------- PCOUNT: ", p_count)
        reply = ""
        try:
            data = p_conn.recv(4096).decode()
            if not data:
                break
            else:
                # reset the game
                if data == GAME_RESET:
                    print("data: 'reset' ")

                # do the tile checking
                elif data == GET_BOARD:
                    print("data: client getting board from server")
                    reply = board

                elif data == GAME_PREPSTART:
                    print("Server: Preparing to start the game.")
                    # TODO: check if game can actually start,
                    #  it should broadcast to all clients at the same time
                    if p_count >= 2:
                        reply = GAME_START
                        broadcast(reply)
                        break
                    else:
                        reply = 'Game requires minimum of 2 players.'

                elif data == GAME_PLAY:
                    # normal game info passing
                    pass

                elif data == PLAYER_JOIN:
                    print("data: new player has joined.")
                    player_num = add_client_to_list(p_conn, p_addr)
                    if player_num == -1:
                        break
                    reply = player_num
                    print("player number: ", player_num)


                    # Both of these checks will not allow player to join the game.
                    # if isGameInProgress:
                    #     reply = GAME_IN_PROGRESS
                    if player_num is None:
                        reply = "GameFull"
                        print("-----------   Game is full")

                elif data == PLAYER_DISCONNECT:
                    # todo: remove them in clients, decrement player count
                    print("A client has disconnected.")
                    delete_client_from_list(p_conn, p_addr)

                p_conn.sendall(pickle.dumps(reply))

        except:
            break

    print("[Player %s] - conn.close()" % player_num)
    p_conn.close()


while True:
    conn, addr = s.accept()
    avail_spots = len(free_clients_indices)

    '''START PHASE'''
    # Server begins to start the game
    if gameStart is True:
        if avail_spots < 2:
            gameStart = False

    '''READY PHASE'''
    # gameOn is True when at least one player is connected (initiated the map)
    if gameOn is False:
        print("Starting new game...\nGenerating new map...")
        board = Board(Util.TILEWIDTH, Util.TILEHEIGHT)
        board.initialize_board()
        gameOn = True  # When the first player 'starts' the game, other players just need to join (map generates once)


    start_new_thread(threaded_client, (conn, addr))
