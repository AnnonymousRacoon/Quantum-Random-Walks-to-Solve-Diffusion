from DiffusionProject.Algorithms.Coins import HadamardCoin
from DiffusionProject.Algorithms.Walks import QuantumWalk, QuantumWalk1D, QuantumWalk2D, QuantumWalk3D
from DiffusionProject.Backends.backend import Backend
from DiffusionProject.Algorithms.Boundaries import BoundaryControl, Boundary
from DiffusionProject.Evaluation.Plotter import plot_distribution2D, plot_distribution3D, plot_distribution1D
from DiffusionProject.Utils.timer import Timer
import pandas as pd
import subprocess



class Experiment:
    
    def __init__(self,backend: Backend, n_dims,n_qubits,shots,max_iterations,stepsize, coin_class = HadamardCoin, experiment_name = None) -> None:
        self.n_dims = n_dims
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
        self.boundary_control = BoundaryControl()
        self.boundary_control.add_boundaries(self.boundaries)

        # initialise walk
        self.walk = QuantumWalk(backend, self.system_dims,self.initial_states,coin_class=coin_class,boundary_controls=[self.boundary_control])
        self.walk.step()

        self._set_path(experiment_name)

    def _set_path(self,experiment_name: None):
        # name experiment
        self.coin_name = str(self.walk.shift_coin._name).split()[0]
        if experiment_name is None:
            self.path = "Experiment_{}_dims_{}_qubits_{}_coin".format(self.n_dims,self.n_qubits,self.coin_name)
        else:
            self.path = experiment_name

    def _build_filetree(self):
        subprocess.run("mkdir {}".format(self.path), shell=True)
        subprocess.run("mkdir {}/images".format(self.path), shell=True)
        subprocess.run("mkdir {}/data".format(self.path), shell=True)
        subprocess.run("mkdir {}/debug".format(self.path), shell=True)

    def _plot_distribution(self, experiment_number, results, plot_path):
        if self.n_dims == 2:
            title = "diffusion on an {0}x{0} grid with a {1} after {2} steps".format(2**self.n_qubits, self.walk.shift_coin._name,experiment_number)
            plot_distribution2D(results=results,n_qubits=self.n_qubits,savepath=plot_path,title=title)
        elif self.n_dims == 3:
            title = "diffusion on an {0}x{0}*{0} grid with a {1} after {2} steps".format(2**self.n_qubits, self.walk.shift_coin._name,experiment_number)
            plot_distribution3D(results=results,n_qubits=self.n_qubits,savepath=plot_path,title=title)


    def _run_experiment(self):
        """runs a monte carlo simulation after a varied number of timesteps specified by `self.stepsize` and `self.max_iterations`"""
        debug_file_path = self.path + 'debug/debug.txt'
        with open(debug_file_path, 'w') as f:
            f.write('Debug output for a {} coined walk on a {} dimensional system with {} qubit dimensions:\n'.format(self.coin_name,self.n_dims,self.n_qubits))
        # begin experiment
        for experiment_number in range(1,self.max_iterations+1,self.stepsize):

            experiment_name = "{}D_Walk_{}_bit_iteration_{}_{}".format(self.n_dims,2**self.n_qubits,experiment_number, self.walk.shift_coin._name)
            data_path = self.path + "/data/{}_results.csv".format(experiment_name)
            plot_path = self.path + "/images/{}.png".format(experiment_name)
            
            # save and plot results
            results = self.walk.get_results(shots=self.shots)
            results = pd.DataFrame(results)
            results.to_csv(data_path)
            self._plot_distribution(experiment_number=experiment_number, results=results, plot_path=plot_path)

            # get covariance
            covariance_matrix = self.walk.get_covariance_tensor()

            # output diffusion tensor to debig output
            print("diffusion tensor after {} timesteps\n".format(experiment_number))
            print(covariance_matrix)
            with open(debug_file_path, 'a') as f:
                f.write("\ndiffusion tensor after {} timesteps\n".format(experiment_number))
                f.write('{}'.format(covariance_matrix))

            self.walk.add_n_steps(self.stepsize)

        print("Experiment Completed!")

    def run(self):
        """runs a monte carlo simulation after a varied number of timesteps specified by `self.stepsize` and `self.max_iterations`"""
        self._build_filetree()
        self._run_experiment()

class Experiment2D(Experiment):
    """Depricated"""

    def __init__(self, backend: Backend, n_qubits, shots, max_iterations, stepsize, coin_class = HadamardCoin, experiment_name = None) -> None:
        super().__init__(backend, 2, n_qubits, shots, max_iterations, stepsize, coin_class, experiment_name)

        # initialise walk
        self.walk = QuantumWalk2D(self.system_dims,self.initial_states,coin_class=coin_class,boundary_controls=[self.boundary_control])
        self.walk.step()

    def _plot_distribution(self, experiment_number, results, plot_path):
        title = "diffusion on an {0}x{0} grid with a {1} after {2} steps".format(2**self.n_qubits, self.walk.shift_coin._name,experiment_number)
        plot_distribution2D(results=results,n_qubits=self.n_qubits,savepath=plot_path,title=title)


    def _run_experiment(self):
        print("Experimenting in {} dimensions with on a {}*{} closed grid and a {}".format(self.n_dims,2**self.n_qubits,2**self.n_qubits, self.walk.shift_coin._name))
        return super()._run_experiment()

class Experiment3D(Experiment):
    """Depricated"""
    
    def __init__(self, backend: Backend, n_qubits, shots, max_iterations, stepsize, coin_class = HadamardCoin, experiment_name = None) -> None:
        super().__init__(backend, 3, n_qubits, shots, max_iterations, stepsize, coin_class, experiment_name)

        # initialise walk
        self.walk = QuantumWalk3D(self.system_dims,self.initial_states,coin_class=coin_class,boundary_controls=[self.boundary_control])
        self.walk.step()

    def _plot_distribution(self, experiment_number, results, plot_path):
        title = "diffusion on an {0}x{0}*{0} grid with a {1} after {2} steps".format(2**self.n_qubits, self.walk.shift_coin._name,experiment_number)
        plot_distribution3D(results=results,n_qubits=self.n_qubits,savepath=plot_path,title=title)


    def _run_experiment(self):
        print("Experimenting in {0} dimensions with on a {1}*{1}*{1} closed grid and a {2}".format(self.n_dims,2**self.n_qubits, self.walk.shift_coin._name))
        return super()._run_experiment()

class debugExperiment(Experiment):
    """runs a simple debug experiment - Depricated"""
    def __init__(self, backend: Backend, n_dims, coin_class=HadamardCoin, experiment_name=None) -> None:
        n_qubits = 2
        shots = 128
        max_iterations = 1
        stepsize = 1
        super().__init__(backend, n_dims, n_qubits, shots, max_iterations, stepsize, coin_class, experiment_name)

class SingleExperiment(Experiment):

    def __init__(self, walk : QuantumWalk, n_dims, n_qubits, shots, n_steps,decoherence_intervals = None, experiment_name=None, directory_path = ".") -> None:
        self.walk = walk
        self.n_steps = n_steps
        self.n_dims = n_dims
        self.n_qubits = n_qubits
        self.shots = shots
        self.directory_path = directory_path
        self.job_id_path = self.directory_path +'/' + "IBM_job_list.txt"
        self._set_path(experiment_name)
        self.decoherence_intervals = decoherence_intervals

    def _set_path(self,experiment_name: None):
        # name experiment
        self.coin_name = str(self.walk.shift_coin._name).split()[0]
        if experiment_name is None:
            self.path = self.directory_path +'/' + "Experiment_{}_dims_{}_qubits_{}_coin".format(self.n_dims,self.n_qubits,self.coin_name)
        else:
            self.path = self.directory_path +'/' + experiment_name

    def _plot_distribution(self, results, plot_path):
        if self.n_dims == 1:
            title = "diffusion on an {0} digit line with a {1}".format(2**self.n_qubits, self.walk.shift_coin._name)
            plot_distribution1D(results=results,n_qubits=self.n_qubits,savepath=plot_path,title=title)
        if self.n_dims == 2:
            title = "diffusion on an {0}x{0} grid with a {1}".format(2**self.n_qubits, self.walk.shift_coin._name)
            plot_distribution2D(results=results,n_qubits=self.n_qubits,savepath=plot_path,title=title)
        elif self.n_dims == 3:
            title = "diffusion on an {0}x{0}*{0} grid with a {1}".format(2**self.n_qubits, self.walk.shift_coin._name)
            plot_distribution3D(results=results,n_qubits=self.n_qubits,savepath=plot_path,title=title)

    def _run_experiment_locally(self):
        """Run a quantum walk experiment on local hardware"""
        timer = Timer()
        timer.start()

        if self.decoherence_intervals:
            results,qiskit_time = self.walk.run_decoherence_experiment(n_steps=self.n_steps, decoherence_intervals = self.decoherence_intervals, shots=self.shots,return_elapsed_time=True)
        else:
            job = self.walk.run_experiment(n_steps=self.n_steps, shots=self.shots)
            results, qiskit_time = self.walk.get_results(job,True)

        python_elapsed_time = Timer.seconds_to_hms(timer.stop())
        print(python_elapsed_time)
        
        self._process_results(results,qiskit_time)

    def submit_job_to_IBM(self):

        job = self.walk.run_experiment(n_steps=self.n_steps, shots=self.shots)
        job_id = job.job_id()

        with open(self.job_id_path, 'a') as f:
            f.write("JOBID:{}".format(job_id))

        print("JOB ID: {} submitted succesfully!".format(job_id))

        circuit_diagram_path = self.path + "/circuit_diagram.png"
        self.walk.draw_debug(circuit_diagram_path)



    def _process_completed_IBM_job(self):

        with open(self.job_id_path, 'r') as f:
            job_id = f.readline().split(":")[1]
        
        results, qiskit_time = self.walk.load_results_from_IBM(job_id, True)
        self._process_results(results,qiskit_time)




    def _process_results(self,results,elapsed_time):
        experiment_name = "{}D_Walk_{}_bit_{}_{}_steps".format(self.n_dims,2**self.n_qubits, self.walk.shift_coin._name,self.n_steps)
        debug_file_path = self.path + '/debug/debug_{}.txt'.format(experiment_name)
        with open(debug_file_path, 'w') as f:
            f.write('\nDebug output for a {} coined walk on a {} dimensional system with {} qubit dimensions after {} steps:\n'.format(self.coin_name,self.n_dims,self.n_qubits,self.n_steps))
        # begin experiment
        

       
        data_path = self.path + "/data/{}_results.csv".format(experiment_name)
        plot_path = self.path + "/images/{}.png".format(experiment_name)
        circuit_diagram_path = self.path + "/circuit_diagram.png"
      

        results = pd.DataFrame(results)
        results.to_csv(data_path)
        self._plot_distribution(results=results, plot_path=plot_path)

        # draw the circuit
        self.walk.draw_debug(circuit_diagram_path)

        # get covariance
        covariance_matrix = self.walk.get_covariance_tensor()

        # output diffusion tensor to debig output
        print("Elapsed experiment time: {} ".format(Timer.seconds_to_hms(elapsed_time)))
        print("diffusion tensor\n")
        print(covariance_matrix)
        with open(debug_file_path, 'a') as f:
            f.write("\nElapsed experiment time: {}\n".format(Timer.seconds_to_hms(elapsed_time)))
            f.write("diffusion tensor\n")
            f.write('{}'.format(covariance_matrix))


        print("Experiment Completed!")



    def run_locally(self):
        """runs a monte carlo simulation after a varied number of timesteps specified by `self.stepsize` and `self.max_iterations`"""
        self._build_filetree()
        self._run_experiment_locally()

    def process_IBM_results(self):
        self._build_filetree()
        self._process_completed_IBM_job()
