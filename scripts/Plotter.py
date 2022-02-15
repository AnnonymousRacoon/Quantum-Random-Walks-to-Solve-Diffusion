from qiskit import *
import pandas as pd
import numpy as np
usim = Aer.get_backend('aer_simulator')
from qiskit.circuit.library.standard_gates import HGate, XGate
from qiskit.circuit import ControlledGate
from matplotlib import pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")

# from Walks import *
from Coins import HadamardCoin, GroverCoin
from Walks import QuantumWalk, Boundary, QuantumWalk1D, QuantumWalk2D, OneWayBoundary


pd.DataFrame
n_qubits = 4
boundaries = []

# apply hard boundary
for dimension, bitstring in zip([0,0,1,1],["0001","1110","0001","1110"]):
    
    boundaries.append(Boundary(bitstring,dimension=dimension))

# apply soft boundary
# for dimension, bitstring, name in zip([0,0,1,1],["1010","0100","1010","0100"],["left","right",'down','up']):
    
#     boundaries.append(OneWayBoundary(bitstring = bitstring,dimension=dimension,n_boundary_cycle_bits=3, label=name))

walk = QuantumWalk2D([n_qubits,n_qubits],["0111","0111"],coin_class=HadamardCoin,boundaries=boundaries)
walk.step()
# walk.add_n_steps(20)


for experiment_number in range(1,30):
    print("running experiment {}".format(experiment_number))
    results = walk.get_results(shots=512)
    x,y,alpha = results["dimension_0"],results["dimension_1"],results["probability_density"]
    plt.scatter(x,y,alpha=[i**(1/n_qubits) for i in alpha],linewidths=[20*(i*n_qubits)**0.5 for i in alpha], s = [400*(i*n_qubits)**0.5 for i in alpha])
    plt.xlim(0,15)
    plt.ylim(0,15)
    plt.plot([10,10],[0,15],"orange")
    plt.plot([4,4],[0,15],"orange")
    plt.plot([0,15],[10,10],"orange")
    plt.plot([0,15],[4,4],"orange")

    plt.plot([1,1],[0,15],"purple")
    plt.plot([14,14],[0,15],"purple")
    plt.plot([0,15],[1,1],"purple")
    plt.plot([0,15],[14,14],"purple")

    plt.xlim(0, 15)
    plt.ylim(0, 15)
    plt.xlabel('X')
    plt.ylabel('Y')
    # plt.title('diffusion with a soft boundary')



    plt.savefig("DiffusionProject/scripts/plots/reversible_exp{}.png".format(experiment_number),dpi = 300)
    plt.cla()
    walk.step()
   