from .genome import Genome, cross_genomes
from .utils import *

from operator import attrgetter
import random
import math


class Species:
    spec_id = 0

    def __init__(self, gen):
        self.exemplar = gen.copy() # The exemplar needs to persist.
        self.genomes = [gen]
        self.adj_fitness = 0.0
        self.staleness = 0
        self.max_fitness = 0.0
        self.ID = Species.spec_id
        Species.spec_id += 1

    def calc_new_fitness(self):
        self.adj_fitness = 0.0
        num_genomes = len(self.genomes)

        for gen in self.genomes:
            self.adj_fitness += gen.fitness
            gen.adjusted_fitness = gen.fitness / num_genomes

        self.adj_fitness /= float(len(self.genomes))
        return self.adj_fitness

    def update_staleness(self):
        self.genomes = sorted(self.genomes,
                              key=attrgetter('fitness'),
                              reverse=True)
        if self.genomes[0].fitness > self.max_fitness:
            self.max_fitness = self.genomes[0].fitness
            self.staleness = 0
        else:
            self.staleness += 1

    def make_children(self, num_children, added_connections, num_genomes):
        self.genomes = self.genomes[:math.ceil(len(self.genomes)*0.2)]
        self.exemplar = random.choice(self.genomes)
        children = []
        for i in range(num_children):
            if i == 0 and len(self.genomes) >= 5:
                children.append(self.genomes[0].copy())
            else:
                gen1 = random.choice(self.genomes)
                if random.random() < PERCENT_NO_CROSS:
                    children.append(gen1.copy())
                else:
                    gen2 = random.choice(self.genomes)
                    children.append(cross_genomes(gen1, gen2))

        children_out = []

        for i, gen in enumerate(children): # leave the champion unchanged if big species
            if i == 0 and len(self.genomes) > 5:
                children_out.append(gen)
                continue
            gen.init_network()            
            if random.random() < ADD_NODE_CHANCE:
                gen.add_node(added_connections)
            if random.random() < ADD_CONNECTION_CHANCE:
                gen.add_connection(added_connections)
            if random.random() < MUTATE_CHANCE:
                gen.mutate()
            children_out.append(gen)

        return children_out
