from NEAT.neatLearner import NeatLearner
import pickle

GENS = 100

nl = NeatLearner(num_inputs=2, num_outputs=1, num_genomes=100)

for i in range(GENS):
    nl.start_generation()
