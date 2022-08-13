import socket
import _pickle as pickle
from NetworkUtils import IPADDRESS, PORTNUMBER


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = IPADDRESS
        self.port = PORTNUMBER
        self.addr = (self.server, self.port)
        self.player_num = None

    def connect(self):
        try:
            self.client.connect(self.addr)
            return
        except:
            pass

    def send_only(self, data):
        try:
            # self.client.sendall(data)
            self.client.sendall(pickle.dumps(data))
            return
        except socket.error as e:
            print("Error [Network.py]: ", e)

    # When sending to Server, it will also hear back from the server
    def send(self, data):
        try:
            # self.client.sendall(data)
            self.client.sendall(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048 * 2))
        except socket.error as e:
            print("Error [Network.py]: ", e)

    def recv(self):
        try:
            return pickle.loads(self.client.recv(2048 * 2))
        except:
            # pass # Do nothing
            return None

    def disconnect(self):
        try:
            self.client.close()
        except:
            pass

    def set_player_num(self, num):
        self.player_num = num

    def get_player_num(self):
        return self.player_num
