import math

_C1 = 1.0
# C2 from the paper omitted
_C3 = 1.0


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
    diff = _avg_diff(big, small)
    return (_C1 * disjoint)/N + _C3*diff


def _num_disjoint(gen1, gen2):
    disjoint = 0.0
    for conn in gen1.connections:
        if conn not in gen2.connections:
            disjoint += 1.0

    for conn in gen2.connections:
        if conn not in gen1.connections:
            disjoint += 1.0

    return disjoint


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
