import numpy as np

from mesa import Model
from mesa.agent import Agent
from mesa.time import RandomActivation
from mesa.space import SingleGrid
import random

transition_matrix = np.array([
    [0.7, 0.2, 0.1],  # Normal to (Normal, Suspicious, Malicious)
    [0.4, 0.5, 0.1],  # Suspicious to (Normal, Suspicious, Malicious)
    [0.1, 0.3, 0.6]   # Malicious to (Normal, Suspicious, Malicious)
])

def next_state(current_state, transition_matrix):
    return np.random.choice([0, 1, 2], p=transition_matrix[current_state])

def generate_states(initial_state, steps, transition_matrix):
    states = [initial_state]
    for _ in range(steps - 1):
        states.append(next_state(states[-1], transition_matrix))
    return states

class NetworkNode(Agent):
    def __init__(self, unique_id, model, is_malicious=False):
        super().__init__(model)
        self.unique_id = unique_id
        self.is_malicious = is_malicious
        self.state = 0

    def step(self):
        self.state = next_state(self.state, self.model.transition_matrix)
        traffic_type = ["normal", "suspicious", "malicious"][self.state]
        self.model.traffic.append({"node": self.unique_id, "type": traffic_type})

class NetworkModel(Model):
    def __init__(self, n_nodes, n_malicious, transition_matrix):
        super().__init__()  # Initialize the Model base class
        self.n_nodes = n_nodes
        self.n_malicious = n_malicious
        self.random = random.Random()
        self.schedule = RandomActivation(self)
        self.transition_matrix = transition_matrix
        self.grid = SingleGrid(10, 10, torus=False)
        self.traffic = []

        # Add nodes
        for i in range(n_nodes):
            is_malicious = i < n_malicious
            node = NetworkNode(i, self, is_malicious)
            self.schedule.add(node)

    def step(self):
        self.traffic = []
        self.schedule.step()

model = NetworkModel(n_nodes=10, n_malicious=2, transition_matrix=transition_matrix)
for i in range(5):
    model.step()
    print(model.traffic)


from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.node import RemoteController

class SimpleTopo(Topo):
    def build(self):
        switch = self.addSwitch('s1')
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        self.addLink(h1, switch)
        self.addLink(h2, switch)

net = Mininet(topo=SimpleTopo(), controller=RemoteController)
remote_controller = net.addController(
        'remote',
        controller=RemoteController,
        ip='127.0.0.1',  # Docker container's host network IP
        port=6633        # Default OVS port
    )
# net = Mininet(topo=SimpleTopo())
net.start()
net.pingAll()
net.stop()
