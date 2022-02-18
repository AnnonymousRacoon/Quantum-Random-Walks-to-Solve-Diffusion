from DiffusionProject.Algorithms.Coins import HadamardCoin
from DiffusionProject.Algorithms.Walks import Boundary,QuantumWalk, QuantumWalk1D, QuantumWalk2D, QuantumWalk3D, OneWayBoundary
from DiffusionProject.Evaluation.Plotter import plot_distribution2D, plot_distribution3D
import pandas as pd
import subprocess


class Experiment:
    
    def __init__(self,n_dims,n_qubits,shots,max_iterations,stepsize, coin_class = HadamardCoin) -> None:
        self.n_dims
        self.n_qubits = n_qubits
        self.shots = shots
        self.max_iterations = max_iterations
        self.stepsize = stepsize

        self.middle_bitstring = "0"+"1"*(n_qubits-1)
        self.initial_states = [self.middle_bitstring]*n_dims
        self.system_dims = [n_qubits]*n_dims

        # add edge boundaries
        self.boundaries = []
        for dimension in range(n_dims):
            for bin_value in ["0","1"]:
                bitstring = bin_value*n_qubits
                self.boundaries.append(Boundary(bitstring,dimension=dimension))

        self.walk = QuantumWalk(self.system_dims,self.initial_states,coin_class=coin_class,boundaries=self.boundaries)
        self.walk.step()

    def _build_filetree(self):
        subprocess.run("mkdir images", shell=True)
        subprocess.run("mkdir data", shell=True)

    def _plot_distribution(self, experiment_number, results, plot_path):
        if self.n_dims == 2:
            title = "diffusion on an {0}x{0} grid with a {1} after {2} steps".format(2**self.n_qubits, self.walk.shift_coin._name,experiment_number)
            plot_distribution2D(results=results,n_qubits=self.n_qubits,savepath=plot_path,title=title)
        elif self.n_dims == 3:
            title = "diffusion on an {0}x{0}*{0} grid with a {1} after {2} steps".format(2**self.n_qubits, self.walk.shift_coin._name,experiment_number)
            plot_distribution3D(results=results,n_qubits=self.n_qubits,savepath=plot_path,title=title)


    def _run_experiment(self):
        """runs a monte carlo simulation after a varied number of timesteps specified by `self.stepsize` and `self.max_iterations`"""
        # begin experiment
        for experiment_number in range(1,self.max_iterations+1,self.stepsize):

            experiment_name = "{}D_Walk_{}_bit_iteration_{}_{}".format(self.n_dims,2**self.n_qubits,experiment_number, self.walk.shift_coin._name)
            data_path = "data/{}_results.csv".format(experiment_name)
            plot_path = "images/{}.png".format(experiment_name)
            
            results = self.walk.get_results(shots=self.shots)
            print("results after {} timesteps".format(experiment_number))

            # save and plot results
            results = pd.DataFrame(results)
            results.to_csv(data_path)
            self._plot_distribution(experiment_number=experiment_number, results=results, plot_path=plot_path)

            # get covariance
            covariance_matrix = self.walk.get_covariance_tensor()
            print(covariance_matrix)
            self.walk.add_n_steps(self.stepsize)

    def run(self):
        """runs a monte carlo simulation after a varied number of timesteps specified by `self.stepsize` and `self.max_iterations`"""
        self._build_filetree()
        self._run_experiment()

class Experiment2D(Experiment):

    def __init__(self, n_qubits, shots, max_iterations, stepsize, coin_class = HadamardCoin) -> None:
        super().__init__(2, n_qubits, shots, max_iterations, stepsize, coin_class)

        # initialise walk
        self.walk = QuantumWalk2D(self.system_dims,self.initial_states,coin_class=coin_class,boundaries=self.boundaries)
        self.walk.step()

    def _plot_distribution(self, experiment_number, results, plot_path):
        title = "diffusion on an {0}x{0} grid with a {1} after {2} steps".format(2**self.n_qubits, self.walk.shift_coin._name,experiment_number)
        plot_distribution2D(results=results,n_qubits=self.n_qubits,savepath=plot_path,title=title)


    def _run_experiment(self):
        print("Experimenting in {} dimensions with on a {}*{} closed grid and a {}".format(self.n_dims,2**self.n_qubits,2**self.n_qubits, self.walk.shift_coin._name))
        return super().run_experiment()

class Experiment3D(Experiment):
    
    def __init__(self, n_qubits, shots, max_iterations, stepsize, coin_class = HadamardCoin) -> None:
        super().__init__(3, n_qubits, shots, max_iterations, stepsize, coin_class)

        # initialise walk
        self.walk = QuantumWalk3D(self.system_dims,self.initial_states,coin_class=coin_class,boundaries=self.boundaries)
        self.walk.step()

    def _plot_distribution(self, experiment_number, results, plot_path):
        title = "diffusion on an {0}x{0}*{0} grid with a {1} after {2} steps".format(2**self.n_qubits, self.walk.shift_coin._name,experiment_number)
        plot_distribution3D(results=results,n_qubits=self.n_qubits,savepath=plot_path,title=title)


    def _run_experiment(self):
        print("Experimenting in {0} dimensions with on a {1}*{1}*{1} closed grid and a {2}".format(self.n_dims,2**self.n_qubits, self.walk.shift_coin._name))
        return super().run_experiment()
