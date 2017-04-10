import random

_MUTATE_POWER = 1.0

def get_next_connection_id():
    next_id = Connection.next_id
    Connection.next_id += 1
    return next_id

class Connection:
    next_id = 0
    def __init__(self, from_node, to_node, ID=-1, is_recurrent=False):
        if ID == -1:
            self.ID = next_id
            next_id += 1
        else:
            self.ID = ID

        self.from_node = from_node
        self.to_node = to_node
        self.weight = random.random() - 0.5
        self.is_recurrent = is_recurrent
        self.is_enabled = True

    def copy(self):
        cpy = Connection(self.from_node, self.to_node, self.ID, self.is_recurrent)
        cpy.weight = self.weight
        cpy.is_enabled = self.is_enabled
        return cpy

    def perturb(self):
        self.weight += random.normalvariate(0, _MUTATE_POWER)

    def reset_weight(self):
        self.weight = random.random() - 0.5

    def __str__(self):
        return ('ID: {},'
                ' From Node: {},'
                ' To Node: {},'
                ' Weight: {}').format(self.ID,
                                     self.from_node,
                                     self.to_node,
                                     self.weight)

    def __eq__(self, other):
        return (self.from_node == other.from_node and
                self.to_node == other.to_node)

    def __ne__(self, other):
        return not self == other
