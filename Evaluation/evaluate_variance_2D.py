
from DiffusionProject.Algorithms.Coins import HadamardCoin, GroverCoin
from DiffusionProject.Algorithms.Walks import Boundary, QuantumWalk1D, QuantumWalk2D, OneWayBoundary
from DiffusionProject.Evaluation.Plotter import plot_distribution2D
import pandas as pd
import subprocess

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

# begin experiment
print("Experimenting in 2 dimensions with on a {}*{} closed grid and a {}".format(2**n_qubits,2**n_qubits, walk.shift_coin._name))
for experiment_number in range(1,max_iterations+1,stepsize):

    experiment_name = "2D_Walk_{}x{}_iteration_{}_{}".format(2**n_qubits,2**n_qubits,experiment_number, walk.shift_coin._name)
    data_path = "data/{}_results.csv".format(experiment_name)
    plot_path = "images/{}.png".format(experiment_name)
    title = "diffusion on an {}x{} grid with a {} after {} steps".format(2**n_qubits,2**n_qubits, walk.shift_coin._name,experiment_number)
    
    results = walk.get_results(shots=shots)
    print("results after {} timesteps".format(experiment_number))

    # save and plot results
    results = pd.DataFrame(results)
    results.to_csv(data_path)
    plot_distribution2D(results=results,n_qubits=n_qubits,savepath=plot_path,title=title)

    # get covariance
    covariance_matrix = walk.get_covariance_tensor()
    print(covariance_matrix)
    walk.add_n_steps(stepsize)
