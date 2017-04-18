from collections import defaultdict
from os.path import join
import pickle
from pprint import pprint
import sys
import matplotlib.pyplot as plt

def process_generation(distribution, generation):
    num_genomes = 0
    num_species = 0

    for l in distribution.values():
        if l[generation] != 0:
            num_genomes += l[generation]
            num_species += 1

    return num_genomes, num_species

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Please supply a directory to process')
        exit()

    directory = sys.argv[1]
    with open(join(directory, 'final.pkl'), 'rb') as f:
        nl = pickle.load(f)

    if nl is None:
        print("Couldn't load pickled file")
        exit()

    print('Num generations:', nl.generations)
    species = {}
    for spec in nl.species:
        species[spec.ID] = spec

    for spec in nl.graveyard:
        species[spec.ID] = spec

    distribution = defaultdict(list)
    print(max(((x.birth,x.ID) for x in species.values())))

    for spec in species.values():
        distribution[spec.ID] = [0] * (spec.birth-1) + spec.genomes_history

    for spec in species.values():
        distribution[spec.ID] += [0] * (nl.generations - len(distribution[spec.ID]))

    spec_over_time = []
    for gen in range(nl.generations):
        spec_over_time.append(process_generation(distribution, gen)[1])

    plt.plot(spec_over_time)
    plt.xlabel('Generation')
    plt.ylabel('Species')
    plt.title('Species Over Time')
    plt.axhline(y=40, color='r')
    plt.savefig(join(directory, 'time_species.png'))
    plt.close()
