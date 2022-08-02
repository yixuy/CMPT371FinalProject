import socket
import pickle


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = 'localhost'
        self.port = 50000
        self.addr = (self.server, self.port)
        # self.p = self.connect()

    def getP(self):
        return 12
        # return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            pass

    # When sending to Server, it will also hear back from the server
    def send(self, data):
        try:
            # return self.client.send(data.encode())
            self.client.send(data.encode())
            # return self.client.recv(2048).decode()
            # self.client.send(str.encode(data))
            # response = pickle.loads(self.client.recv(2048*2))
            return pickle.loads(self.client.recv(2048*2))
        except socket.error as e:
            print("Error [Network.py]: ", e)

    # def recv(self):
    #     try:
    #         return self.client.recv(2048).decode()
    #     except:
    #         pass

    def disconnect(self):
        try:
            self.client.close()
        except:
            pass