
from DiffusionProject.Algorithms.Coins import GroverCoin
from DiffusionProject.Evaluation.Experiments import Experiment3D
from DiffusionProject.Algorithms.Walks import Backend

# experiment settings
stepsize = 199
max_iterations = 200
n_qubits = 9
shots = 2048
BACKEND = Backend(use_GPU=False)

experiment = Experiment3D(BACKEND, n_qubits=n_qubits,shots=shots,max_iterations=max_iterations,stepsize=stepsize,coin_class=GroverCoin)
experiment.run()