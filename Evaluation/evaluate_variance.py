
from DiffusionProject.Algorithms.Coins import HadamardCoin, GroverCoin
from DiffusionProject.Algorithms.Walks import QuantumWalk, Boundary, QuantumWalk1D, QuantumWalk2D, OneWayBoundary
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")


n_qubits = 8
boundaries = []

# apply hard boundary
for dimension, bitstring in zip([0,0,1,1],["00000001","11111110","00000001","11111110"]):
    
    boundaries.append(Boundary(bitstring,dimension=dimension))


walk = QuantumWalk2D([n_qubits,n_qubits],["01111111","01111111"],coin_class=HadamardCoin,boundaries=boundaries)
walk.step()
# walk.add_n_steps(20)



stepsize = 10
print("Experimenting in 2 dimensions with on a {}*{} closed grid and a {}".format(2**n_qubits,2**n_qubits, walk.shift_coin._name))
for experiment_number in range(1,11,stepsize):
    print("results after {} timesteps".format(experiment_number))
    results = walk.get_results(shots=2048)

    # save_results
    results = pd.DataFrame(results)
    results.to_csv("2D_Walk_{}x{}_iteration_{}_{}_results.csv".format(2**n_qubits,2**n_qubits,experiment_number, walk.shift_coin._name))

    covariance_matrix = walk.get_covariance_tensor()
    print(covariance_matrix)
    walk.add_n_steps(stepsize)


    




    # plt.savefig("DiffusionProject/scripts/plots/reversible_exp{}.png".format(experiment_number),dpi = 300)
    # plt.cla()
    # walk.step()
   
