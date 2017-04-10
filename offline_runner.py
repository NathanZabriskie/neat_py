from NEAT.neatLearner import NeatLearner

import pickle
import numpy as np
from scipy.spatial.distance import euclidean
from os.path import join
import tqdm

GENERATIONS = 150
GENOMES = 200
SAVE_DIR = 'results/run2'

TRAIN_INPUTS = np.array([[0.0,0.0],
                         [1.0,0.0],
                         [0.0,1.0],
                         [1.0,1.0]])

TRAIN_OUTPUTS = np.array([[0.0],
                          [1.0],
                          [1.0],
                          [0.0]])

nl = NeatLearner(num_inputs=2, num_outputs=1, num_genomes=GENOMES, allow_recurrent=False)
pkl_file = join(SAVE_DIR, 'backup.pkl')
best_fitness = 0.0
for generation in range(GENERATIONS):
    nl.start_generation()
    for g in range(GENOMES):
        error = 0.0
        outputs = []
        for i, inputs in enumerate(TRAIN_INPUTS):
            out = nl.get_output(inputs=inputs, genome=g)
            outputs.append(out)
            error += euclidean(TRAIN_OUTPUTS[i], out)
        fitness = (4.0-error)*(4.0-error)
        nl.assign_fitness(fitness=fitness, genome=g)
        if fitness > best_fitness:
            best_fitness = fitness
            print('New Best:', best_fitness)
            if fitness > 8.0:
                print('want to cry')

    nl.end_generation()

    if generation % 5 == 0:
        nl.save_top_genome('gen{}'.format(generation), SAVE_DIR)
        with open(pkl_file, 'wb') as f:
            pickle.dump(nl, f)

nl.save_top_genome('gen{}'.format(GENERATIONS), SAVE_DIR)
with open(pkl_file, 'wb') as f:
            pickle.dump(nl, f)
