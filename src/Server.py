import socket
import time
import datetime
from _thread import *
from threading import _pickle as pickle   # This is pickle with c implementation (a lot faster) vs python based Timer

import GameLogic.Util as Util
from GameLogic.Board import Board
import GameLogic.Util as Util
from NetworkUtils import *

MAX_PLAYERS = 4
player_count = 0
are_players_ready = False
is_game_running = False
board = None

free_clients_indices = [0, 1, 2, 3]
clients = [None] * len(free_clients_indices)

timer = None
is_timer_running = False
remaining_game_time = REMAINING_TIME_MSG + str(TOTAL_GAME_TIME_IN_SECONDS) + "s"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((IPADDRESS, PORTNUMBER))
except socket.error as e:
    str(e)

# queue up as many as 4 connect requests (the normal max)
# before refusing outside connections.
s.listen(4)  # Queue up to max 4 requests (in case of burst connections)
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


def add_client_to_list(p_conn, p_addr):
    global player_count
    print("Server: using add_client_to_list()")
    # clients format: [ [conn, ip, port], [conn, ip, port], etc ], etc ]
    # Note: clients indices are kept the same (even when removed)

    # This is to check if client is already connected (to counter the potential bugs on client side)
    conn_item_list = [[p_conn, p_addr[0], p_addr[1]]]
    check = any(True for i in clients if i in conn_item_list)
    if check:
        return -1

    if len(free_clients_indices) > 0:
        player_count += 1
        free_clients_indices.sort()  # so the smallest player number is preferred
        to_use_i = free_clients_indices.pop(0)
        clients[to_use_i] = [p_conn, p_addr[0], p_addr[1]]
        player_num = to_use_i + 1  # bcs indices start from 0
        return player_num
    return None


def delete_client_from_list(p_conn, p_addr):
    try:
        for x in range(0, len(clients)):
            print("clients x: ", x)
            if clients[x] is None:
                continue
            if clients[x][0] == p_conn:
                clients[x] = None
                free_clients_indices.append(x)
                player_count -= 1
                p_conn.close()
                print("Client deleted successfully! free_clients_indices added back to list: ", x)
                break
    except:
        pass


def broadcast(msg):
    print("clients: ", clients)
    for client in clients:
        if client is not None:
            my_conn = client[0]
            my_conn.send(pickle.dumps(msg))
    print("Finished broadcast()")


def threaded_client(p_conn, p_addr):
    print("SERVER: In threaded_client thread")
    player_num = 0
    while True:

        reply = {}
        try:
            data = pickle.loads(p_conn.recv(2048))

            if len(data) <= 0:      # Watch out if this break statement causes any unintended problems
                print("THREAD: message is empty")
                delete_client_from_list(p_conn, p_addr)
                break
            else:
                data_code = data["code"]

                # reset the game
                if data_code == GAME_RESET:
                    print("data: 'reset' ")
                    reply["code"] = "Game reset"

                # do the tile checking
                elif data_code == GET_BOARD:
                    # print("data: client getting board from server")
                    reply["code"] = BOARD
                    reply["data"] = board

                elif data_code == GAME_PREPSTART:
                    print("Server: Preparing to start the game.")
                    if player_count >= 2:
                        board.set_cell(0, 0, 1)
                        if player_count == 2:
                            print("CELL IS SET HEREE")
                            board.set_cell(15, 0, 2)
                        if player_count == 3:
                            board.set_cell(15, 0, 2)
                            board.set_cell(0, 15, 3)
                        if player_count == 4:
                            board.set_cell(15, 0, 2)
                            board.set_cell(0, 15, 3)
                            board.set_cell(15, 15, 4)
                        print("Server: Initiating GAME_START")
                        reply["code"] = GAME_START
                        reply["data"] = board
                        print(reply)
                        broadcast(reply)
                        continue
                    else:
                        reply["code"] = GAME_NOT_ENOUGH_PLAYERS

                # When player makes a move, server updates the board, and sends back the new board
                elif data_code == GAME_PLAY:
                    p_col = int(data["player"])
                    p_x = int(data["x"])
                    p_y = int(data["y"])
                    move = data["move"]
                    if move == Util.LEFT and board.get_item(p_x-1, p_y) == 0:
                        board.set_cell(p_x-1, p_y, p_col)
                    elif move == Util.RIGHT and board.get_item(p_x+1, p_y) == 0:
                        board.set_cell(p_x+1, p_y, p_col)
                    elif move == Util.UP and board.get_item(p_x, p_y-1) == 0:
                        board.set_cell(p_x, p_y-1, p_col)
                    elif move == Util.DOWN and board.get_item(p_x, p_y+1) == 0:
                        board.set_cell(p_x, p_y+1, p_col)
                    board.print_board()
                    print()
                    reply["code"] = BOARD
                    reply["data"] = board
                    broadcast(reply)
                    continue

                elif data_code == PLAYER_JOIN:
                    print("data: new player has joined.")
                    player_num = add_client_to_list(p_conn, p_addr)
                    if player_num == -1:
                        print("player could not join.")
                        break
                    reply = player_num
                    print("player number: ", player_num)


                    # Both of these checks will not allow player to join the game.
                    # if isGameInProgress:
                    #     reply = GAME_IN_PROGRESS
                    if player_num is None:
                        reply["code"] = GAME_FULL
                        print("-----------   Game is full")

                elif data_code == PLAYER_DISCONNECT:
                    # todo: remove them in clients, decrement player count
                    print("[Player %s]: A client has disconnected." % player_num)
                    delete_client_from_list(p_conn, p_addr)
                    break

                elif data == REMAINING_GAMETIME:
                    reply = remaining_game_time

                p_conn.sendall(pickle.dumps(reply))

        except EOFError as err:
            delete_client_from_list(p_conn, p_addr)
            break

        except Exception as err:
            print('Server - Reading error: {}'.format(str(err)))
            continue


    print("[Player %s] - conn.close()" % player_num)
    # p_conn.close()


def reset_timer():
    global is_timer_running, timer
    is_timer_running = False
    if timer is not None and timer.is_alive():
        timer.cancel()


def start_timer():
    global is_timer_running, timer
    is_timer_running = True
    game_duration = datetime.datetime.strptime(time.strftime("%H:%M:%S"), "%H:%M:%S") + \
                    datetime.timedelta(0, TOTAL_GAME_TIME_IN_SECONDS + 1)

    def display(msg):
        global remaining_game_time
        remaining_seconds = int(
            (game_duration - datetime.datetime.strptime(time.strftime("%H:%M:%S"), "%H:%M:%S")).total_seconds())
        message = msg + str(remaining_seconds) + "s"
        print(message)
        remaining_game_time = message

    class RepeatTimer(Timer):
        def run(self):
            while not self.finished.wait(self.interval):
                self.function(*self.args, **self.kwargs)

    timer = RepeatTimer(1, display, [REMAINING_TIME_MSG])
    timer.start()
    time.sleep(TOTAL_GAME_TIME_IN_SECONDS + 2)  # Let the timer "run" for the duration of the game until it reaches '0'
    timer.cancel()


while True:
    connection, address = s.accept()
    avail_spots = len(free_clients_indices)

    if not is_timer_running:
        start_new_thread(start_timer, ())

    """START PHASE"""
    # Server begins the game
    if is_game_running is True:
        # if not timer_running:
        #     start_timer()
        if avail_spots < 2:
            is_game_running = False
            # reset_timer()  # reset the timer
    else:  # Game is not running as the flag is false; reset the timer
        # reset_timer()
        pass

    """READY PHASE"""
    # player_ready is True when at least one player is connected (initiated the map)
    if are_players_ready is False:
        print("Starting new game...\nGenerating new map...")
        board = Board(Util.TILEWIDTH, Util.TILEHEIGHT)
        board.initialize_board()
        board.print_board()
        are_players_ready = True  # When the first player 'starts' the game, other players just need to join (map generates once)


    start_new_thread(threaded_client, (connection, address))
