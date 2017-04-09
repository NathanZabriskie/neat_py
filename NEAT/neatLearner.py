from .utils import *

import operator
import math
import random

_MUTATE_CONNS_CHANCE = 0.8
_CONN_PERTURB_CHANCE = 0.9

_ADD_NODE_CHANCE = 0.03
_ADD_LINK_CHANCE = 0.3

_DeltaDist = 3.0

_MAX_STALENESS = 15

class NeatLearner:
    def __init__(self,
                 num_inputs,
                 num_outputs,
                 num_genomes):
        self.num_inputs = num_inputs + 1 # add in a bias node
        self.num_outputs = num_outputs
        self.num_genomes = num_genomes

        self.genomes = []
        self.species = []

        self.init_genomes()
        Connection.next_id = self.num_inputs + self.num_outputs - 1

    def init_genomes(self):
        print('Initializing ' + str(self.num_genomes) + ' genomes.')
        for i in range(self.num_genomes):
            self.genomes.append(Genome(self.num_inputs, self.num_outputs))

    def start_generation(self):
        for gen in self.genomes:
            gen.init_network()

    def end_generation(self):
        self.assign_species()
        self.assign_offspring()

    def assign_species(self):
        for spec in self.species:
            spec.genomes = []

        for gen in self.genomes:
            for spec in self.species:
                if get_genome_distance(gen, spec.exemplar) < _DeltaDist:
                    spec.genomes.append(gen)
                    break
            else:
                self.species.append(Species(gen))

    def assign_offspring(self):
        total_fitness = 0.0
        for spec in self.species:
            total_fitness += spec.calc_fitness()

    def get_output(self, inputs, genome):
        return self.genomes[genome].get_output(inputs)

    def assign_fitness(self, fitness, genome):
        self.genomes[genome].fitness = fitness

    def __str__(self):
        return ('NeatLearner:\n'
                '\tNum Inputs: {}\n'
                '\tNum Outputs: {}\n'
                '\tNum Genomes: {}\n\n'
                'Genomes:\n{}').format(self.num_inputs,
                                         self.num_outputs,
                                         self.num_genomes,
                                         '\n\n'.join((str(x)
                                                    for x in self.genomes)))


class Species:
    def __init__(self, gen):
        self.exemplar = gen.copy() # The exemplar needs to persist.
        self.genomes = []
        self.adj_fitness = 0.0
        self.staleness = 0
        self.max_fitness = 0.0

    def calc_fitness(self):
        if not self.genomes:
            return 0.0

        self.adj_fitness = 0.0
        for gen in self.genomes:
            self.adj_fitness += gen.fitness

        self.adj_fitness /= float(len(self.genomes))
        return self.adj_fitness

    def make_offspring(self, num_children):
        children = []
        if num_children == 0:
            return children

        self.genomes = sorted(self.genomes,
                              key=operator.attrgetter('fitness'),
                              reverse=True)
        if not self.genomes or self.genomes[0].fitness < self.max_fitness:
            self.staleness += 1
        else:
            self.staleness = 0
            self.max_fitness = self.genomes[0].fitness
            

class Genome:
    def __init__(self, num_inputs, num_outputs):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.connections = {}
        self.nodes = {}
        self.fitness = 0.0

        self.outputs = [i+self.num_inputs for i in range(num_outputs)]
        self.inputs = [i for i in range(num_inputs)]
        self.init_connections()

    def copy(self):
        cpy = Genome(self.num_inputs, self.num_outputs)
        cpy.fitness = self.fitness
        cpy.connections = {}

        for conn_id in self.connections:
            conn = self.connections[conn_id]
            cpy.connections[conn_id] = Connection(from_node=conn.from_node,
                                                   to_node=conn.to_node,
                                                   ID=conn.ID,
                                                   is_recurrent=conn.is_recurrent)
            cpy.connections[conn_id].weight = conn.weight

        return cpy

    def __str__(self):
        fit = 'Current Fitness: ' + str(self.fitness)
        conns = (str(x) for x in self.connections.values())
        return fit + '\nConnections\n' + '\n'.join(conns)

    def init_connections(self):
        con_id = 0
        for i in self.inputs:
            for j in self.outputs:
                newCon = Connection(i, j, con_id)
                con_id += 1
                self.connections[newCon.ID] = newCon

    def init_network(self):
        self.nodes = {}
        for conn in self.connections.values():
            if conn.from_node not in self.nodes:
                self.nodes[conn.from_node] = Node()

            if conn.to_node not in self.nodes:
                self.nodes[conn.to_node] = Node()

            self.nodes[conn.to_node].incoming_connections.append(conn.ID)

    def get_output(self, inputs):
        assert len(inputs) + 1 == self.num_inputs
        inputs.append(1.0) # Append the bias term to the input array.
        for node in self.nodes.values():
            node.last_out = node.out
            node.out = 0.0
            node.has_output = False

        for i, val in enumerate(inputs): # Set the input nodes' values.
            self.nodes[i].out = val
            self.nodes[i].has_output = True

        output = []
        for i in self.outputs:
            output.append(self.get_node_output(i))
        return output

    def get_node_output(self, node_num):
        node = self.nodes[node_num]
        net = 0.0
        for inc in (self.connections[x] for x in node.incoming_connections):
            if not inc.is_enabled:
                continue
            in_node_id = inc.from_node
            in_node = self.nodes[in_node_id]
            if inc.is_recurrent:
                net += inc.weight * in_node.last_out
            elif in_node.has_output:
                net += inc.weight * in_node.out
            else:
                net += inc.weight * self.get_node_output(in_node_id)

        node.has_output = True
        node.out = sigmoid(net)
        return node.out

    def _is_input(self, check_id):
        return check_id < self.num_inputs

    def _is_output(self, check_id):
        return check_id > self.num_inputs


class Connection:
    next_id = 0
    def __init__(self, from_node, to_node, ID=-1, is_recurrent=False):
        if ID == -1:
            self.ID = next_id
            next_id += 1
        else:
            self.ID = ID

        self.from_node = from_node
        self.to_node = to_node
        self.weight = random.normalvariate(mu=0.0, sigma=0.1)
        self.is_recurrent = is_recurrent
        self.is_enabled = True

    def __str__(self):
        return ('ID: {},'
                ' From Node: {},'
                ' To Node: {},'
                ' Weight: {}').format(self.ID,
                                     self.from_node,
                                     self.to_node,
                                     self.weight)

    def __eq__(self, other):
        return (self.from_node == other.from_node and
                self.to_node == other.to_node)

    def __ne__(self, other):
        return not self == other


class Node:
    def __init__(self):
        self.out = 0.0
        self.last_out = 0.0
        self.incoming_connections = []
        self.has_output = False
