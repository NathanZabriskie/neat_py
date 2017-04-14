from NEAT.neatLearner import NeatLearner
from NEAT.utils import unison_shuffle, print_hyperparameters
from arff_loader import load_arff

import matplotlib.pyplot as plt
import numpy as np
from os.path import join, exists
import pickle
from scipy.spatial.distance import euclidean
import shutil
import tqdm


GENERATIONS = 200
GENOMES = 200

SAVE_DIR = 'results/ionosphere_long'
DATASET = 'data/ionosphere.arff'

def XOR():
    inputs = np.array([[0.0,0.0],
                       [1.0,0.0],
                       [0.0,1.0],
                       [1.0,1.0]])

    labels = np.array([[0.0],
                       [1.0],
                       [1.0],
                       [0.0]])

    return inputs, labels

def measure_test_acc(learner, data, labels):
    accuracy = 0.0
    for i, t in enumerate(test_data):
        out = learner.get_best_output(t)
        if len(out) == 1: # binary class
            if out[0] < 0.5 and test_labels[i][0] < 0.5:
                accuracy += 1.0
            elif out[0] > 0.5 and test_labels[i][0] > 0.5:
                accuracy += 1
        else:
            if np.argmax(out) == np.argmax(test_labels[i]):
                accuracy += 1.0

    accuracy /= test_data.shape[0]
    accuracy *= 100
    return accuracy

def split_sets(data, labels, percent=0.8):
    num_train = int(data.shape[0] * percent)
    train_data = data[0:num_train]
    train_labels = labels[0:num_train]

    test_data = data[num_train+1:]
    test_labels = labels[num_train+1:]

    return (train_data,
            train_labels,
            test_data,
            test_labels)

if exists(SAVE_DIR):
    choice = input(('Save directory {} exists, do you want '
                   'to remove it and continue? [y/n]\n').format(SAVE_DIR))
    if choice == 'y':
        shutil.rmtree(SAVE_DIR)
    else:
        print('Exiting')
        exit()

inputs, labels = load_arff(DATASET, normalize=True)
inputs, labels = unison_shuffle(inputs, labels)
train_data, train_labels, test_data, test_labels = split_sets(inputs,labels)
nl = NeatLearner(num_inputs=train_data.shape[1],
                 num_outputs=train_labels.shape[1],
                 num_genomes=GENOMES,
                 allow_recurrent=False)

pkl_file = join(SAVE_DIR, 'backup.pkl')
best_fitness = -9999999.0
accuracy_hist = []
num_species = []
max_fitness = train_labels.shape[0] * train_labels.shape[1]
print(max_fitness)
for generation in range(GENERATIONS):
    nl.start_generation()
    print('\nStarting Generation:', nl.generations)
    for g in range(GENOMES):
        error = 0.0
        for i, inputs in enumerate(train_data):
            out = nl.get_output(inputs=inputs, genome=g)
            error += euclidean(train_labels[i], out)
        fitness = max_fitness - error
        nl.assign_fitness(fitness=fitness, genome=g)


    nl.end_generation()
    accuracy = measure_test_acc(nl, test_data, test_labels)
    accuracy_hist.append(accuracy)

    if nl.best_genome.fitness > best_fitness:
        best_fitness = nl.best_genome.fitness
        print('New Best:', best_fitness)
        nl.save_genome(SAVE_DIR, 'best', g)
        print('New Accuracy: {:.02}'.format(accuracy))
    species = len(nl.species)
    num_species.append(species)
    print('Num Species:', species)

    if generation % 5 == 0:
        nl.save_top_genome(SAVE_DIR, 'gen{}'.format(generation))
        nl.save_species_exemplars(join(SAVE_DIR, 'gen_'+str(generation)))
        with open(pkl_file, 'wb') as f:
            pickle.dump(nl, f)

accuracy = measure_test_acc(nl, test_data, test_labels)
print('Final Accuracy: {:.2f}%'.format(accuracy))

with open(join(SAVE_DIR, 'summary.txt'), 'w') as f:
    f.write('Dataset: {}\n'.format(DATASET))
    f.write('Generations: {}\n'.format(GENERATIONS))
    f.write('GENOMES: {}\n'.format(GENOMES))
    f.write('Final Accuracy: {:.02f}%\n'.format(accuracy))
    f.write(print_hyperparameters())

with open(pkl_file, 'wb') as f:
    pickle.dump(nl, f)

plt.plot(accuracy_hist)
plt.ylabel('Highest Fitness Accuracy')
plt.xlabel('Generation')
plt.savefig(join(SAVE_DIR, 'accuracy.png'))
plt.close()

plt.plot(num_species)
plt.ylabel('Num Species')
plt.xlabel('Generation')
plt.savefig(join(SAVE_DIR, 'num_species.png'))
plt.close()
