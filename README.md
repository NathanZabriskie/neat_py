# NeuroEvolution of Augmenting Topologies

An implementation of the NeuroEvolution of Augmenting Topologies ([NEAT](http://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf)) 
algorithm written in Python as part of CS 678 - Advanced Neural Networks at BYU. 

NEAT is a genetic algorithm that works by evolving a node network starting from a topology that includes only input nodes, output nodes,
and a bias. For more details on the algorithm see the paper linked above.

This repository includes functions to run the algorithm offline on arff files as well as in live reinforcement learning 
environments. The meat of the actual algorithm is implemented in the NEAT package while the files in the top level actually run
the algorithm. 

[gym_test.py](https://github.com/NathanZabriskie/neat_py/blob/master/gym_test.py) shows how to hook up neat_py to environments
from the [open ai gym](https://github.com/openai/gym). The gif below shows an example agent produced by the algorithm that
was able to solve the pole balancing problem without being given the current velocity of the cart or the pole.

![Final cart pole solution](https://github.com/NathanZabriskie/neat_py/blob/master/report/images/pole_final.gif)

Here is the network representation of the agent where green nodes are inputs, blue is output, red lines indicate
recurrent connections (meaning the output of the connection is delayed for one timestep), and dashed lines represent
disabled connections.

![cart pole solution network](https://github.com/NathanZabriskie/neat_py/blob/master/report/images/cart_pole_final.png)

In order to support the maximum number of environments, 
[remote_runner.py](https://github.com/NathanZabriskie/neat_py/blob/master/remote_runner.py) spins up a simple web server and 
listens for commands sent from a remote client. This was done so that neat_py could talk to a Lua script running in the
[Bizhawk emulator](http://tasvideos.org/Bizhawk.html). Using this setup neat_py was used to train an agent to play 
a NES port of Flappy Bird running in the emulator. The fittest agents were able to play the game indefinitely.

![NEAT learning to play Flappy Bird](https://github.com/NathanZabriskie/neat_py/blob/master/report/images/flappy.PNG)

For more detailed information about neat_py's performance and experiments performed using this implementation see the 
project [writeup](https://github.com/NathanZabriskie/neat_py/blob/master/report/writeup.pdf).
