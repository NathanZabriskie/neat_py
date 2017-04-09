class Node:
    def __init__(self):
        self.out = 0.0
        self.last_out = 0.0
        self.incoming_connections = []
        self.has_output = False
