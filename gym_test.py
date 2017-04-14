from NEAT.neatLearner import NeatLearner
from NEAT.utils import print_hyperparameters


import gym
import matplotlib.pyplot as plt
from os.path import join, exists
import pickle
import shutil
import time

env = gym.make('CartPole-v1')
SOLUTION_ITERATIONS = 100
SOLUTION_FOUND = 475.0

NUM_GENOMES = 1000
NO_VELOCITY = True
RENDER = False

SAVE_DIR = 'results/polenovel_long_no_v2'
pkl_file = join(SAVE_DIR, 'backup.pkl')

def check_solution(genome):
    fitness = 0.0
    print('Checking solution')
    for _ in range(SOLUTION_ITERATIONS):
        observation = env.reset()
        done = False
        while not done:
            if RENDER:
                env.render()
            out = nl.get_output(get_input(observation), genome)
            action = 0 if out < 0.5 else 1
            observation, reward, done, info = env.step(action)
            fitness += reward

    avg_fitness = fitness / SOLUTION_ITERATIONS
    print('Avg fitness ', str(avg_fitness))
    return avg_fitness > SOLUTION_FOUND, avg_fitness

def save_and_exit(generations, neatLearner, best_fitness_hist, seconds):
    with open(join(SAVE_DIR, 'summary.txt'), 'w') as f:
        f.write('Trained in {} generations\n'.format(generations))
        f.write('Trained in {:.4f} seconds\n'.format(seconds))
        f.write('Num Genomes: {}\n'.format(NUM_GENOMES))
        f.write('Include Velocity: {}\n'.format(not NO_VELOCITY))
        f.write(print_hyperparameters())

    with open(join(SAVE_DIR, 'final.pkl'), 'wb') as f:
        pickle.dump(neatLearner, f)

    with open(join(SAVE_DIR, 'fitness.pkl'), 'wb') as f:
        pickle.dump(best_fitness_hist, f)

    exit()

def get_input(observation):
    if NO_VELOCITY:
        return [observation[0], observation[2]]
    else:
        return observation

if __name__ == '__main__':
    start_time = time.time()
    if exists(SAVE_DIR):
        choice = input(('Save directory {} exists, do you want '
                       'to remove it and continue? [y/n]\n').format(SAVE_DIR))
        if choice == 'y':
            shutil.rmtree(SAVE_DIR)
        else:
            print('Exiting')
            exit()

    if NO_VELOCITY:
        nl = NeatLearner(2, 1, NUM_GENOMES, True)
    else:
        nl = NeatLearner(4, 1, NUM_GENOMES, False)

    best_fitness = 0.0
    generation = 0
    best_fitness_hist = []

    while True:
        nl.start_generation()
        print('Starting Generation {}'.format(nl.generations))

        for genome in range(NUM_GENOMES):
            fitness = 0.0
            observation = env.reset()
            done = False
            while not done:
                if RENDER:
                    env.render()
                out = nl.get_output(get_input(observation), genome)
                action = 0 if out < 0.5 else 1
                observation, reward, done, info = env.step(action)
                fitness += reward
                if fitness > 499:
                    winner, avg = check_solution(genome)
                    fitness += avg * 2
                    if winner:
                        print('Found a winner!')
                        nl.best_genome = nl.genomes[genome]
                        nl.assign_fitness(fitness, genome)
                        nl.save_top_genome(SAVE_DIR, 'best')
                        best_fitness_hist.append(fitness)
                        save_and_exit(generation,
                                      nl,
                                      best_fitness_hist,
                                      time.time() - start_time)

            nl.assign_fitness(fitness, genome)

        generation += 1
        nl.end_generation()
        print('Num species: {}'.format(len(nl.species)))

        if nl.best_genome.fitness > best_fitness:
            best_fitness = nl.best_genome.fitness
            print('New Best:', best_fitness)
            nl.save_top_genome(SAVE_DIR, 'best')

        best_fitness_hist.append(best_fitness)

        if generation % 30 == 0:
            nl.save_top_genome(SAVE_DIR, 'gen{}'.format(generation))
            nl.save_species_exemplars(join(SAVE_DIR, 'gen_'+str(generation)))
            with open(pkl_file, 'wb') as f:
                pickle.dump(nl, f)
