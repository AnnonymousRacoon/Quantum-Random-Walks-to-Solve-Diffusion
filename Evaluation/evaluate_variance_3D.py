from DiffusionProject.Algorithms.Coins import HadamardCoin, GroverCoin
from DiffusionProject.Evaluation.Experiments import Experiment3D

# experiment settings
stepsize = 10
max_iterations = 150
n_qubits = 7
shots = 2048

experiment = Experiment3D(n_qubits=n_qubits,shots=shots,max_iterations=max_iterations,stepsize=stepsize,coin_class=HadamardCoin)
experiment.run()

experiment = Experiment3D(n_qubits=n_qubits,shots=shots,max_iterations=max_iterations,stepsize=stepsize,coin_class=GroverCoin)
experiment.run()
