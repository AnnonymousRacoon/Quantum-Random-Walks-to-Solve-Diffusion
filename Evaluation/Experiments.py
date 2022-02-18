from DiffusionProject.Algorithms.Coins import HadamardCoin, GroverCoin
from DiffusionProject.Algorithms.Walks import Boundary, QuantumWalk1D, QuantumWalk2D, OneWayBoundary
from DiffusionProject.Evaluation.Plotter import plot_distribution2D
import pandas as pd
import subprocess


class Experiment:
    
    def __init__(self) -> None:
        pass



# build_filetree
subprocess.run("mkdir images", shell=True)
subprocess.run("mkdir data", shell=True)

# experiment settings
stepsize = 10
max_iterations = 100
n_qubits = 7
n_dims = 2
shots = 2048

# initial states
middle_bitstring = "0"+"1"*(n_qubits-1)
initial_states = [middle_bitstring]*n_dims
system_dims = [n_qubits]*n_dims

# apply hard boundary at edges
boundaries = []
for dimension in range(n_dims):
    for bin_value in ["0","1"]:
        bitstring = bin_value*n_qubits
        boundaries.append(Boundary(bitstring,dimension=dimension))

# initialise walk
walk = QuantumWalk2D(system_dims,initial_states,coin_class=HadamardCoin,boundaries=boundaries)
walk.step()
