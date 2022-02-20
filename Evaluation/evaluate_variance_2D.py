
from DiffusionProject.Algorithms.Coins import HadamardCoin, GroverCoin
from DiffusionProject.Evaluation.Experiments import Experiment2D

# experiment settings
stepsize = 2
max_iterations = 10
n_qubits = 3
shots = 2048

experiment = Experiment2D(n_qubits=n_qubits,shots=shots,max_iterations=max_iterations,stepsize=stepsize,coin_class=HadamardCoin)
experiment.run()

experiment = Experiment2D(n_qubits=n_qubits,shots=shots,max_iterations=max_iterations,stepsize=stepsize,coin_class=GroverCoin)
experiment.run()
