from .connection import Connection, get_next_connection_id
from .node import Node
from .utils import *

import graphviz as gv
import numpy as np
import random


def cross_genomes(gen1, gen2):
    if gen2.fitness > gen1.fitness:
        gen1, gen2 = gen2, gen1

    child = gen1.copy()
    for conn in gen1.connections:
        if conn in gen2.connections:
            if random.random() < 0.5:
                child.connections[conn].weight = gen2.connections[conn].weight

    return child

class Genome:
    def __init__(self, num_inputs, num_outputs, allow_recurrent):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.allow_recurrent = allow_recurrent
        self.connections = {}
        self.nodes = {}
        self.fitness = 0.0

        self.outputs = set([i+self.num_inputs for i in range(num_outputs)])
        self.inputs = set([i for i in range(num_inputs)])
        self.init_connections()

    def copy(self):
        cpy = Genome(self.num_inputs, self.num_outputs, self.allow_recurrent)
        cpy.fitness = self.fitness
        cpy.connections = {}

        for conn_id in self.connections:
            conn = self.connections[conn_id]
            cpy.connections[conn_id] = conn.copy()

        return cpy

    def mutate(self):
        for conn in (self.connections[x] for x in self.connections):
            if random.random() < CONN_PERTURB_CHANCE:
                conn.perturb()
            else:
                conn.reset_weight()

            if not conn.is_enabled and random.random() < REENABLE_CHANCE:
                conn.is_enabled = True
            elif conn.is_enabled and random.random() < DISABLE_CHANCE:
                conn.is_enabled = False

    def add_node(self, added_connections):
        split_conn = self.connections[random.choice(list(self.connections.keys()))]
        new_node_num = max(self.nodes) + 1
        was_enabled = split_conn.is_enabled
        split_conn.is_enabled = False
        new_incoming = Connection(from_node=split_conn.from_node,
                                  to_node=new_node_num,
                                  ID=0,
                                  is_recurrent=split_conn.is_recurrent) # Need to check if this connection has already been added

        new_incoming.weight = 1.0
        for conn in added_connections:
            if conn == new_incoming:
                new_incoming.ID = conn.ID
                break
        else:
            new_incoming.ID = get_next_connection_id()
            added_connections.append(new_incoming)
            
        self.connections[new_incoming.ID] = new_incoming
        self.connections[new_incoming.ID].is_enabled = was_enabled

        new_outgoing = Connection(from_node=new_node_num,
                                  to_node=split_conn.to_node,
                                  ID=0,
                                  is_recurrent=split_conn.is_recurrent)
        
        new_outgoing.weight = split_conn.weight
        for conn in added_connections:
            if conn == new_outgoing:
                new_outgoing.ID = conn.ID
                break
        else:
            new_outgoing.ID = get_next_connection_id()
            added_connections.append(new_outgoing)

        self.connections[new_outgoing.ID] = new_outgoing
        self.connections[new_outgoing.ID].is_enabled = was_enabled        

    def add_connection(self, added_connections):
        from_node = random.randint(0, len(self.nodes)-1)
        to_node = random.randint(0, len(self.nodes)-1)
        while to_node in self.inputs:
            to_node = random.randint(0, len(self.nodes)-1)

        newCon = Connection(from_node=from_node,
                            to_node=to_node,
                            ID=0)
        for conn in (self.connections[x] for x in self.connections):
            if newCon == conn: # not going to bother trying another combination
                return

        if not self.allow_recurrent and (newCon.from_node in self.outputs or
                                         newCon.from_node == newCon.to_node):
            return

        for conn in added_connections:
            if newCon == conn:
                newCon.ID = conn.ID
                break
        else:
            newCon.ID = get_next_connection_id()
            added_connections.append(newCon)

        self.connections[newCon.ID] = newCon
        self.init_network() # rebuild network to include new connection        
        self.check_recurrent()

    def check_recurrent(self):
        visited = set()
        stk = set()
        for conn in self.connections:
            self.connections[conn].is_recurrent = False
        for node_id in self.outputs:
            self.mark_cycles(node_id, visited, stk)

    def mark_cycles(self, node_id, visited, stk):
        if node_id not in visited:
            visited.add(node_id)
            stk.add(node_id)

            incoming_connections = self.nodes[node_id].incoming_connections
            for inc in (self.connections[x] for x in incoming_connections):
                if inc.from_node not in visited:
                    self.mark_cycles(inc.from_node, visited, stk)
                elif inc.from_node in stk:
                    self.connections[inc.ID].is_recurrent = True

        stk.discard(node_id)

    def __str__(self):
        fit = 'Current Fitness: ' + str(self.fitness)
        node = '\nNum Nodes: {}'.format(len(self.nodes))
        conns = (str(x) for x in self.connections.values())
        return fit + node + '\nConnections\n' + '\n'.join(conns)

    # TODO: Remove ideal network creation
    def init_connections(self):
        con_id = 0
        for i in self.inputs:
            for j in self.outputs:
                newCon = Connection(i, j, con_id)
                con_id += 1
                self.connections[newCon.ID] = newCon

                '''newCon = Connection(i,4, con_id)
                con_id += 1
                self.connections[newCon.ID] = newCon

        for out in self.outputs:
            newCon = Connection(4,out,con_id)
            con_id += 1
            self.connections[newCon.ID] = newCon'''

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
        inputs = np.append(inputs, [1.0])
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
        return np.array(output)

    def get_node_output(self, node_num):
        node = self.nodes[node_num]
        net = 0.0
        for inc in (self.connections[x] for x in node.incoming_connections):
            if not inc.is_enabled:
                continue
            in_node_id = inc.from_node
            in_node = self.nodes[in_node_id]
            if inc.is_recurrent:
                if self.allow_recurrent:
                    net += inc.weight * in_node.last_out
            elif in_node.has_output:
                net += inc.weight * in_node.out
            else:
                net += inc.weight * self.get_node_output(in_node_id)

        self.nodes[node_num].has_output = True
        self.nodes[node_num].out = sigmoid(net)
        return self.nodes[node_num].out

    def output_graph(self, outdir, outfile):
        self.init_network()
        g1 = gv.Digraph(format='png')
        
        g1.attr('node', shape='doublecircle')
        for in_node in self.inputs:
            g1.attr('node', color='green')
            g1.node(self.get_node_name(in_node))
        for out_node in self.outputs:
            g1.attr('node', color='blue')
            g1.node(self.get_node_name(out_node))

        g1.attr('node', shape='circle', color='black')
        for node_id in self.nodes:
            if node_id in self.inputs or node_id in self.outputs:
                continue
            g1.node(self.get_node_name(node_id))

        for conn in (self.connections[x] for x in self.connections):
            if not conn.is_enabled:
                g1.attr('edge', style='dashed', arrowhead='empty')
            if conn.is_recurrent:
                g1.attr('edge', color='red')
            g1.edge(self.get_node_name(conn.from_node),
                    self.get_node_name(conn.to_node),
                    label='{:.4f}'.format(conn.weight))
            g1.attr('edge', color='black', arrowhead='normal', style='solid')

        g1.body.append('label = "Fitness = {:.2f}"'.format(self.fitness))
        g1.render(filename=outfile,
                  directory=outdir,
                  cleanup=True)

    def get_node_name(self, node_id):
        if node_id in self.inputs:
            if node_id == len(self.inputs) - 1:
                return 'bias'
            else:
                return 'in_' + str(node_id)
        elif node_id in self.outputs:
            return 'out_' + str(node_id)
        else:
            return 'hidden_' + str(node_id)
