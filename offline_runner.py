from NEAT.neatLearner import NeatLearner
import pickle
import numpy as np
from scipy.spatial.distance import euclidean
from os.path import join

GENERATIONS = 100
GENOMES = 100
SAVE_DIR = 'results/run1'

TRAIN_INPUTS = np.array([[0.0,0.0],
                         [1.0,0.0],
                         [0.0,1.0],
                         [1.0,1.0]])

TRAIN_OUTPUTS = np.array([[0.0],
                          [1.0],
                          [1.0],
                          [0.0]])

nl = NeatLearner(num_inputs=2, num_outputs=1, num_genomes=GENOMES)
pkl_file = join(SAVE_DIR, 'backup.pkl')

for generation in range(GENERATIONS):
    nl.start_generation()
    for g in range(GENOMES):
        error = 0.0
        for i, inputs in enumerate(TRAIN_INPUTS):
            out = nl.get_output(inputs=inputs, genome=g)
            error += euclidean(TRAIN_OUTPUTS[i], out)
        fitness = (4.0-error)**2
        nl.assign_fitness(fitness=fitness, genome=g)
        if fitness > 10:
            print('Something is working!')

    nl.end_generation()

    if generation % 5 == 0:
        nl.save_top_genome('gen{}'.format(generation), SAVE_DIR)
        with open(pkl_file, 'wb') as f:
            pickle.dump(nl, f)
