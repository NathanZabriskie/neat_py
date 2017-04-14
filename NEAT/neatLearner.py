from .connection import Connection
from .genome import Genome
from .species import Species
from .utils import *

from collections import defaultdict
from operator import attrgetter
import math
import random

class NeatLearner:
    def __init__(self,
                 num_inputs,
                 num_outputs,
                 num_genomes,
                 allow_recurrent):
        self.num_inputs = num_inputs + 1 # add in a bias node
        self.num_outputs = num_outputs
        self.num_genomes = num_genomes
        self.allow_recurrent = allow_recurrent

        self.genomes = []

        self.species = []
        self.graveyard = []

        self.generations = 0

        self.best_genome = None

        self._init_genomes()
        Connection.next_id = self.num_inputs + self.num_outputs - 1

    def _init_genomes(self):
        print('Initializing ' + str(self.num_genomes) + ' genomes.')
        for i in range(self.num_genomes):
            self.genomes.append(Genome(self.num_inputs, self.num_outputs, self.allow_recurrent))

    def start_generation(self):
        for gen in self.genomes:
            gen.init_network()

    def adjust_species(self):
        if self.generations <= 1:
            return
        global DeltaDist
        if len(self.species) < SPECIES_TARGET:
            DeltaDist -= DELTA_ADJUSTER
        elif len(self.species) > SPECIES_TARGET:
            DeltaDist += DELTA_ADJUSTER

        DeltaDist = max(DeltaDist, MIN_DISTANCE)

    def end_generation(self):
        self.generations += 1
        self.adjust_species()
        self._update_best_genome()
        self._assign_species(self.generations)
        self._remove_empty_species()
        self._remove_stale_species()
        total_fitness = self._calc_total_fitness()
        new_genomes = []

        added_connections = []
        survived_species = []
        for spec in self.species:
            num_children = math.floor((spec.adj_fitness/total_fitness)
                                      * self.num_genomes)
            if num_children != 0:
                survived_species.append(spec)
                new_genomes += spec.make_children(num_children,
                                                  added_connections,
                                                  self.num_genomes)
            else:
                print('No kids :(')

        self.species = survived_species
        while len(new_genomes) < self.num_genomes:
            spec = random.choice(self.species)
            new_genomes += spec.make_children(1,
                                              added_connections,
                                              self.num_genomes)

        self.genomes = new_genomes

    def _update_best_genome(self):
        if self.best_genome is None:
            self.best_genome = self.genomes[0]

        for gen in self.genomes:
            if gen.fitness > self.best_genome.fitness:
                self.best_genome = gen

    def get_output(self, inputs, genome):
        return self.genomes[genome].get_output(inputs)

    def get_best_output(self, inputs):
        return self.best_genome.get_output(inputs)

    def assign_fitness(self, fitness, genome):
        self.genomes[genome].fitness = fitness

    def save_top_genome(self, outdir, outfile):
        self.best_genome.output_graph(outdir, outfile)

    def save_genome(self, outdir, outfile, genome):
        self.genomes[genome].output_graph(outdir,
                                          outfile)

    def save_species_exemplars(self, outdir):
        for spec in self.species:
            f = 'species{}'.format(spec.ID)
            spec.exemplar.output_graph(outdir,
                                       f,
                                       spec.genomes_history[-1])

    def _assign_species(self, generation):
        for spec in self.species:
            spec.genomes = []

        for gen in self.genomes:
            for spec in self.species:
                if get_genome_distance(gen, spec.exemplar) < DeltaDist:
                    spec.genomes.append(gen)
                    break
            else:
                self.species.append(Species(gen, generation))

    def _remove_empty_species(self):
        spec_out = []
        for spec in self.species:
            if len(spec.genomes) >= 1:
                spec_out.append(spec)
            else:
                self.graveyard.append(spec)
        self.species = spec_out

    def _remove_stale_species(self):
        if len(self.species) == 1:
            return
        spec_out = []
        for spec in self.species:
            spec.update_staleness()
            if spec.staleness < MAX_STALENESS:
                spec_out.append(spec)
            else:
                self.graveyard.append(spec)

        if spec_out:
            self.species = spec_out

    def _calc_total_fitness(self):
        total_fitness = 0.0
        for spec in self.species:
            total_fitness += spec.calc_new_fitness()

        return total_fitness

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
