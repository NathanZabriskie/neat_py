import math
import numpy as np


# Hyper Parameters

'''
MAX_STALENESS = 20

MUTATE_POWER = 2.0

ADD_NODE_CHANCE = 0.03
ADD_CONNECTION_CHANCE = 0.05

PERCENT_NO_CROSS = 0.4
MUTATE_CHANCE = 0.8

CONN_PERTURB_CHANCE = 0.9
REENABLE_CHANCE = 0.2
DISABLE_CHANCE = 0.1

DeltaDist = 3.0
C1 = 1.0
C2 = 1.0
C3 = 0.4

'''
MAX_STALENESS = 20

MUTATE_POWER = 3.0

ADD_NODE_CHANCE = 0.05
ADD_CONNECTION_CHANCE = 0.2

PERCENT_NO_CROSS = 0.4
MUTATE_CHANCE = 0.8

CONN_PERTURB_CHANCE = 0.9
REENABLE_CHANCE = 0.2
DISABLE_CHANCE = 0.1

DeltaDist = 6.0
SPECIES_TARGET = 40
DELTA_ADJUSTER = 0.3
MIN_DISTANCE = 0.3

C1 = 1.5
C2 = 1.5
C3 = 1.5


def unison_shuffle(a, b):
    assert len(a) == len(b)
    p = np.random.permutation(len(a))
    return a[p], b[p]


def sigmoid(net):
    try:
        return 1.0 / (1 + math.exp(-4.9*net))
    except OverflowError:
        return 0.0


def get_genome_distance(gen1, gen2):
    big, small = gen1, gen2
    if len(gen2.connections) > len(gen1.connections):
        big, small = gen2, gen1

    if len(big.connections) < 20:
        N = 1.0
    else:
        N = float(len(big.connections))
    disjoint = _num_disjoint(big, small)
    excess = _num_excess(big, small)
    diff = _avg_diff(big, small)
    return (C1 * disjoint)/N + (C2 * excess)/N + C3*diff


def _num_disjoint(gen1, gen2):
    disjoint = 0.0
    gen1_max = max(list(gen1.connections.keys()))
    gen2_max = max(list(gen2.connections.keys()))

    for conn in gen1.connections:
        if (conn < gen2_max and
                conn not in gen2.connections):
            disjoint += 1.0

    for conn in gen2.connections:
        if (conn < gen1_max and
                conn not in gen1.connections):
            disjoint += 1.0

    return disjoint

def _num_excess(gen1, gen2):
    excess = 0.0
    gen1_max = max(list(gen1.connections.keys()))
    gen2_max = max(list(gen2.connections.keys()))

    if gen2_max > gen1_max:
        gen1, gen2 = gen2, gen1
        gen1_max, gen2_max = gen2_max, gen1_max

    for conn in gen1.connections:
        if conn > gen2_max:
            excess += 1.0
    return excess


def _avg_diff(gen1, gen2):
    num_shared = 0.0
    diff = 0.0
    for conn in gen1.connections:
        if conn in gen2.connections:
            conn1 = gen1.connections[conn]
            conn2 = gen2.connections[conn]
            diff += abs(conn1.weight - conn2.weight)
            num_shared += 1.0

    return diff / num_shared


def print_hyperparameters():
    lines = []
    lines.append('Hyperparameters:')
    lines.append('MAX_STALENESS: {}'.format(MAX_STALENESS))
    lines.append('MUTATE_POWER: {}'.format(MUTATE_POWER))
    lines.append('ADD_NODE_CHANCE: {}'.format(ADD_NODE_CHANCE))
    lines.append('ADD_CONNECTION_CHANCE: {}'.format(ADD_CONNECTION_CHANCE))
    lines.append('PERCENT_NO_CROSS: {}'.format(PERCENT_NO_CROSS))
    lines.append('MUTATE_CHANCE: {}'.format(MUTATE_CHANCE))
    lines.append('CONN_PERTURB_CHANCE: {}'.format(CONN_PERTURB_CHANCE))
    lines.append('REENABLE_CHANCE: {}'.format(REENABLE_CHANCE))
    lines.append('DISABLE_CHANCE: {}'.format(DISABLE_CHANCE))
    lines.append('DeltaDist: {}'.format(DeltaDist))
    lines.append('C1: {}'.format(C1))
    lines.append('C2: {}'.format(C2))
    lines.append('C3: {}'.format(C3))

    return '\n'.join(lines)
