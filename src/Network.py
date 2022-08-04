import pickle
import socket


from NetworkUtils import IPADDRESS, PORTNUMBER


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = IPADDRESS
        self.port = PORTNUMBER
        self.addr = (self.server, self.port)

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            pass

    # When sending to Server, it will also hear back from the server
    def send(self, data):
        try:
            self.client.send(data.encode())
            # return self.client.recv(2048).decode()
            # self.client.send(str.encode(data))
            # response = pickle.loads(self.client.recv(2048*2))
            return pickle.loads(self.client.recv(2048 * 2))
        except socket.error as e:
            print("Error [Network.py]: ", e)

    def disconnect(self):
        try:
            self.client.close()
        except:
            pass
