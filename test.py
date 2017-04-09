import socket
import signal
import json

class UDPClient:
    def __init__(self, port=8080, ip='127.0.0.1'):
        self.port = port
        self.ip = ip
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.ip, self.port))

    def start(self):
        print('Listening on', self.ip + ':' + str(self.port))
        while True:
            data, source = self.s.recvfrom(2048)
            print(json.loads(data))

    def process_msg(self, data):
        print(data)

    def quit(self):
        self.s.close()

if __name__ == '__main__':
    client = UDPClient()
    def signal_handler(signal, frame):
        print("Exiting")
        exit()
    signal.signal(signal.SIGINT, signal_handler)
    client.start()
