
from DiffusionProject.Algorithms.Coins import HadamardCoin
from DiffusionProject.Evaluation.Experiments import Experiment3D

# experiment settings
stepsize = 199
max_iterations = 200
n_qubits = 9
shots = 2048

experiment = Experiment3D(n_qubits=n_qubits,shots=shots,max_iterations=max_iterations,stepsize=stepsize,coin_class=HadamardCoin)
experiment.run()