import pickle
import socket
import time
import datetime
from _thread import *
from threading import Timer

import GameLogic.Util as Util
from GameLogic.Board import Board
from NetworkUtils import *

server = IPADDRESS
port = PORTNUMBER

MAX_PLAYERS = 4
player_count = 0
players_ready = False
game_running = False
board = None

free_clients_indices = [0, 1, 2, 3]
clients = [None] * len(free_clients_indices)

timer_running = False
TOTAL_GAME_TIME_IN_SECONDS = 30
timer = None

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


def add_client_to_list(conn, addr):
    print("Server: using add_client_to_list()")
    # clients format: [ [conn, ip, port], [conn, ip, port], etc ],
    # Note: clients indices are kept the same (even when removed)
    if len(free_clients_indices) > 0:
        free_clients_indices.sort()  # so the smallest player number is preferred
        to_use_i = free_clients_indices.pop(0)
        clients[to_use_i] = [conn, addr[0], addr[1]]
        player_num = to_use_i + 1  # bcs indices start from 0
        return player_num
    return None


def delete_client_from_list(conn, addr):
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
                    # TODO: check if game can actually start, it should broadcast to all clients at the same time
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
                    delete_client_from_list(p_conn, p_addr)

                p_conn.sendall(pickle.dumps(reply))

        except:
            break

    print("conn.close()")
    p_conn.close()


def reset_timer():
    global timer_running, timer
    timer_running = False
    if timer is not None and timer.is_alive():
        timer.cancel()


def start_timer():
    global timer_running, timer
    timer_running = True
    game_duration = datetime.datetime.strptime(time.strftime("%H:%M:%S"), "%H:%M:%S") + \
                    datetime.timedelta(0, TOTAL_GAME_TIME_IN_SECONDS + 1)

    def display(msg):
        remaining_seconds = int(
            (game_duration - datetime.datetime.strptime(time.strftime("%H:%M:%S"), "%H:%M:%S")).total_seconds())
        message = msg + " " + str(remaining_seconds)
        print(message)
        # conn.sendall(pickle.dumps(message))

    class RepeatTimer(Timer):
        def run(self):
            while not self.finished.wait(self.interval):
                self.function(*self.args, **self.kwargs)

    timer = RepeatTimer(1, display, ["Repeating"])
    timer.start()
    print("Threading started")
    time.sleep(TOTAL_GAME_TIME_IN_SECONDS + 2)  # Let the timer "run" for the duration of the game until it reaches '0'
    print("Threading finishing")
    timer.cancel()


while True:
    conn, addr = s.accept()
    avail_spots = len(free_clients_indices)

    if not timer_running:
        start_new_thread(start_timer, ())

    """START PHASE"""
    # Server begins the game
    if game_running is True:
        # if not timer_running:
        #     start_timer()
        if avail_spots < 2:
            game_running = False
            # reset_timer()  # reset the timer
    else:  # Game is not running as the flag is false; reset the timer
        # reset_timer()
        pass

    """READY PHASE"""
    # player_ready is True when at least one player is connected (initiated the map)
    if players_ready is False:
        print("Starting new game...\nGenerating new map...")
        board = Board(Util.TILEWIDTH, Util.TILEHEIGHT)
        board.initialize_board()
        reset_timer()
        # When the first player 'starts' the game, other players just need to join (map generates once)
        players_ready = True

    start_new_thread(threaded_client, (conn, addr))
