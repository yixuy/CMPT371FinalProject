import _pickle as pickle  # This is pickle with c implementation (a lot faster) vs python based Timer
import datetime
import socket
import time
from _thread import *

from GameLogic.Board import Board
from NetworkUtils import *

# Global variables
player_count = 0
are_players_ready = False
is_game_running = False
board = None
game_end_time = None

# To store client's socket information
free_clients_indices = [0, 1, 2, 3]
clients = [None] * len(free_clients_indices)

# Start up Server's socket connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((IPADDRESS, PORTNUMBER))
except socket.error as e:
    str(e)

# queue up as many as 4 connect requests (the normal max)
# before refusing outside connections.
s.listen(MAX_PLAYERS)  # Queue up to max 4 requests (in case of burst connections)
print("Waiting for a connection, Server Started")

"""
Server Summary during Gameplay:
    Receives new coordinates from Player1 (for example)
    Checks new tile coordinates:
        If tile taken:
            Tile colour will not change
            But still broadcast new board map to everyone
        Else if tile not taken:
            Updates the Server tile to the Player1 colour (now tile is taken is taken by Player1 - Tile colour is locked)
            Broadcast new board map to everyone
            
    If either all white tiles are captured or game timer went to 0:
        End the game for clients and close the socket for clients thread in Server
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
        player_num = to_use_i + 1  # b/c indices start from 0, and player number starts from 1
        return player_num
    return None


# If player leaves during Ready Phase, it will free up its player number and close its connection.
def delete_client_from_list(p_conn):
    # clients format: [ [conn, ip, port], [conn, ip, port], etc, None ]
    global player_count
    try:
        for x in range(len(clients)):
            if clients[x] is not None and clients[x][0] == p_conn:
                clients[x] = None
                free_clients_indices.append(x)
                player_count -= 1
                p_conn.close()
                break
    except:
        pass


def broadcast(msg):
    for client in clients:
        if client is not None:
            my_conn = client[0]
            my_conn.send(pickle.dumps(msg))


def threaded_client(p_conn, p_addr):
    global game_end_time
    player_num = 0
    while True:
        reply = {}
        try:
            curr_time = datetime.datetime.now().replace(microsecond=0)

            if game_end_time is not None and game_end_time <= curr_time:
                reply["code"] = GAME_OVER
                reply["data"] = board
                broadcast(reply)
                # Wait for all clients to receive GAME_OVER request so scores can be broadcasted successfully
                time.sleep(2)

            if (game_end_time is not None and game_end_time <= curr_time) or board.is_filled():
                scores = board.get_scores(player_count)
                reply["code"] = DISPLAY_SCORE
                reply["data"] = scores
                broadcast(reply)
                # delete_client_from_list(p_conn)
                break  # break out of the Thread

            data = pickle.loads(p_conn.recv(2048))

            if len(data) <= 0:  # Watch out if this break statement causes any unintended problems
                delete_client_from_list(p_conn)
                break  # break out of the Thread
            else:
                data_code = data["code"]

                if data_code == GET_BOARD:
                    reply["code"] = BOARD
                    reply["data"] = board

                # The player that initiates the Game to start will be the only one to broadcast() to everyone that game will be starting.
                elif data_code == GAME_PREPSTART:
                    if player_count >= 2:
                        board.set_cell(0, 0, 1)
                        if player_count == 2:
                            board.set_cell(Util.TILEWIDTH - 1, 0, 2)
                        if player_count == 3:
                            board.set_cell(Util.TILEWIDTH - 1, 0, 2)
                            board.set_cell(0, Util.TILEHEIGHT - 1, 3)
                        if player_count == 4:
                            board.set_cell(Util.TILEWIDTH - 1, 0, 2)
                            board.set_cell(0, Util.TILEHEIGHT - 1, 3)
                            board.set_cell(Util.TILEWIDTH - 1, Util.TILEHEIGHT - 1, 4)
                        board.decrement_white_tiles_loop(player_count)
                        reply["code"] = GAME_START
                        reply["data"] = board

                        # If first player: Start the server time
                        if game_end_time is None:
                            game_end_time = (datetime.datetime.now() + datetime.timedelta(
                                seconds=SERVER_GAME_TIME_IN_SECONDS)).replace(microsecond=0)

                        broadcast(reply)
                        continue
                    else:
                        reply["code"] = GAME_NOT_ENOUGH_PLAYERS

                # When player makes a move, server updates the board, and sends back the new board to everyone.
                # However, if a player fills in the last white tile, it will broadcast to all players that the Game is over.
                elif data_code == GAME_PLAY:
                    p_col = int(data["player"])
                    p_x = int(data["x"])
                    p_y = int(data["y"])
                    move = data["move"]
                    # White Tile = 0. The Server will set the white tile to player's colour if the tile is white.
                    if move == Util.LEFT and board.get_item(p_x - 1, p_y) == 0:
                        board.set_cell(p_x - 1, p_y, p_col)
                        board.decrement_white_tile()
                    elif move == Util.RIGHT and board.get_item(p_x + 1, p_y) == 0:
                        board.set_cell(p_x + 1, p_y, p_col)
                        board.decrement_white_tile()
                    elif move == Util.UP and board.get_item(p_x, p_y - 1) == 0:
                        board.set_cell(p_x, p_y - 1, p_col)
                        board.decrement_white_tile()
                    elif move == Util.DOWN and board.get_item(p_x, p_y + 1) == 0:
                        board.set_cell(p_x, p_y + 1, p_col)
                        board.decrement_white_tile()

                    # In the case of player captures the last white tile, initiate GAME OVER.
                    if board.is_filled():
                        reply["code"] = GAME_OVER
                        reply["data"] = board
                    else:
                        board.print_board()
                        print()
                        reply["code"] = BOARD
                        reply["data"] = board

                    broadcast(reply)
                    continue

                # When a player ready up, the Server will add the player's socket information to the clients list
                # And reply the player back its player number
                # However, if Game is already full (i.e. Already has 4 players ready in the game), player will not be added and play
                elif data_code == PLAYER_JOIN:
                    player_num = add_client_to_list(p_conn, p_addr)
                    reply["code"] = PLAYER_CAN_JOIN
                    reply["data"] = player_num

                    if player_num == -1:
                        reply["code"] = GAME_FULL

                elif data_code == PLAYER_DISCONNECT:
                    delete_client_from_list(p_conn)
                    break

                p_conn.sendall(pickle.dumps(reply))

        except EOFError as err:
            delete_client_from_list(p_conn)
            break

        except Exception as err:
            print('Server - Reading error: {}'.format(str(err)))
            continue

    print("[Player %s] - conn.close()" % player_num)


while True:
    connection, address = s.accept()

    '''READY PHASE'''
    # When the first player starts up the game, other players just need to join (map generates once)
    # are_players_ready is True when at least one player is connected (initiated the map)
    if are_players_ready is False:
        print("Starting new game...\nGenerating new map...")
        board = Board(Util.TILEWIDTH, Util.TILEHEIGHT)
        board.initialize_board()
        board.print_board()
        are_players_ready = True

    start_new_thread(threaded_client, (connection, address))
