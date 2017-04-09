from NEAT.neatLearner import Species, Genome
import random


gens = [Genome(1,2) for i in range(100)]
for gen in gens:
    gen.fitness = random.randint(0,1000)

spec = Species(gens[0])
spec.genomes = gens
spec.make_offspring(100)

for g in spec.genomes:
    print(g.fitness)
