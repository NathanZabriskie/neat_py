from NEAT.neatLearner import NeatLearner
from NEAT.utils import print_hyperparameters

import pickle
import socket
import signal
import json
from os.path import join

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
            except socket.timeout:
                continue
            data = json.loads(data)
            res = self.process_msg(data)
            json_obj = json.dumps(res)
            self.s.sendto(json_obj.encode('utf-8'), source)

    def process_msg(self, data):
        command = data['command']
        if command == 'init':
            return self.init(data['args'])
        elif command == 'start_gen':
            print('Starting generation')
            self.NL.start_generation()
            return OK
        elif command == 'end_gen':
            print('Ending generation')
            self.NL.end_generation()
            print('Best Fitness: {}'.format(self.NL.best_genome.fitness))
            print('Num Species: {}\n'.format(len(self.NL.species)))
            return OK
        elif command == 'get_output':
           return self.get_output(data['args'])
        elif command == 'save_best':
            return self.save_best(data['args'])
        elif command == 'assign_fitness':
            self.NL.assign_fitness(**data['args'])
            return OK
        elif command == 'save_backup':
            self.backup(**data['args'])
            return OK
        elif command == 'load_backup':
            self.backup(**data['args'])
            return OK
        elif command == 'save_species':
            self.NL.save_species_exemplars(**data['args'])
            return OK
        elif command == 'set_best':
            self.set_best(**data['args'])
            return OK

    def init(self, args):
        self.NL = NeatLearner(**args)
        return OK

    def get_output(self, args):
        out = self.NL.get_output(**args)
        res = OK
        res['result'] = list(out)
        return res

    def save_best(self, args):
        print('Saving best')
        self.NL.save_top_genome(**args)
        return OK

    def quit(self):
        print('Closing socket')
        self.s.close()

    def backup(self, outdir, outfile):
        with open(join(outdir, outfile), 'wb') as f:
            pickle.dump(self.NL, f)

        with open(join(outdir, 'summary.txt'), 'w') as f:
            f.write(print_hyperparameters())
            f.write('\n')

    def load_backup(self, outdir, outfile):
        with open(join(outdir, outfile), 'rb') as f:
            self.NL = pickle.load(f)

    def set_best(self, genome):
        self.NL.best_genome = self.NL.genomes[genome]

if __name__ == '__main__':
    client = NeatUDPClient()
    def signal_handler(signal, frame):
        print("Exiting")
        client.quit()
        exit()
    signal.signal(signal.SIGINT, signal_handler)
    client.start()
