from NEAT.neatLearner import NeatLearner

import socket
import signal
import json

OK = {'status':'OK'}

class NeatUDPClient:
    def __init__(self, port=8080, ip='127.0.0.1'):
        self.port = port
        self.ip = ip
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.ip, self.port))
        self.s.settimeout(1.0)
        self.NL = None

    def start(self):
        print('Listening on', self.ip + ':' + str(self.port))
        while True:
            try:
                data, source = self.s.recvfrom(2048)
                print(source)
            except socket.timeout:
                continue
            data = json.loads(data)
            res = self.process_msg(data)
            json_obj = json.dumps(res)
            self.s.sendto(json_obj.encode('utf-8'), source)
            print(json.dumps(res))

    def process_msg(self, data):
        command = data['command']
        if command == 'init':
            return self.init(data['args'])
        elif command == 'start_gen':
            print('Starting generation')
            self.NL.start_generation()
            return OK
        elif command == 'end_gen':
            self.NL.end_generation()
            return OK
        elif command == 'get_output':
           return self.get_output(data['args'])
        elif command == 'save_best':
            return self.save_best(data['args'])

    def init(self, args):
        self.NL = NeatLearner(**args)
        return OK

    def get_output(self, args):
        out = self.NL.get_output(**args)
        res = OK
        res['result'] = list(out)
        return res

    def save_best(self, args):
        self.NL.save_top_genome(**args)
        return OK

    def quit(self):
        print('Closing socket')
        self.s.close()

if __name__ == '__main__':
    client = NeatUDPClient()
    def signal_handler(signal, frame):
        print("Exiting")
        client.quit()
        exit()
    signal.signal(signal.SIGINT, signal_handler)
    client.start()
