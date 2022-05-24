
import math
from qiskit import QuantumCircuit, QuantumRegister, transpile, assemble
from qiskit.tools.visualization import circuit_drawer
import pandas as pd
from DiffusionProject.Algorithms.Coins import HadamardCoin, CylicController, AbsorbingControl
from DiffusionProject.Algorithms.Boundaries import Boundary, BoundaryControl, AbsorbingBoundaryControl, Obstruction, ControlledDirectionalBoundaryControl, UniDirectionalBoundaryControl, NonDisruptiveBoundaryControl, EfficientBoundaryControl

from DiffusionProject.Backends.backend import Backend
from DiffusionProject.Algorithms.Decoherence import CoinDecoherenceCycle

from numpy import pi

    
class QuantumWalk:

    def __init__(self,backend: Backend ,system_dimensions: list, initial_states: list = None, n_shift_coin_bits: int = None, coin_class = None, coin_kwargs = {}, boundary_controls = [], coin_decoherence_cycle: CoinDecoherenceCycle = None) -> None:
        """
        Create a new `QuantumWalk` Object
        Args:
            backend (`DiffusionProject.Algorithms.Walks.Backend`): The Qiskit backend to run the simulation on\n
            system_dimensions ([int]): a list of the number of qubits used to represent each succesive dimension. e.g for a 2qubitx3qubit system pass in [2,3]\n
            initial_states ([str]) a list of bitsrings to represent the initial state of the system. e.g ["100","110"]. If no arguments are passed the system will start in all 0 states

        
        """

        # qiskit sim backend
        self.backend = backend

        self.coin_decoherence_cycle = coin_decoherence_cycle

        # initialise dimensional states:
        self.state_registers = []
        self.system_dimensions = system_dimensions
        self.n_system_dimensions = len(self.system_dimensions)

        for idx, n_qubits in enumerate(system_dimensions):
            register_name = "dimension{}".format(idx)
            self.state_registers.append(QuantumRegister(n_qubits,register_name))

        # initialise boundary control registers:
        self.boundary_controls = boundary_controls
        self.boundary_control_registers = []
        self.ancilla_registers = []

        self.absorption_register = None
        for boundary_control in self.boundary_controls:
            for boundary in boundary_control.boundaries:

                # For obstruction check both dims
                if type(boundary) == Obstruction:
                    for dim, n_bits in zip(boundary.dimensions, boundary.n_bits):
                        assert dim >= 0 and dim < len(self.system_dimensions)
                        assert n_bits == self.system_dimensions[dim]
                        
                # for other boundaries check single dim
                else:
                    assert boundary.dimension >= 0 and boundary.dimension < len(self.system_dimensions)
                    assert boundary.n_bits == self.system_dimensions[boundary.dimension]
            if boundary_control.ctrl is not None and type(boundary_control) != AbsorbingBoundaryControl:
                self.boundary_control_registers.append(boundary_control.register)

            if boundary_control.ancilla_register:
                ancilla_idx = len(self.ancilla_registers)
                boundary_control.ancilla_register._name += f"{ancilla_idx}"
                self.ancilla_registers.append(boundary_control.ancilla_register)

            # add absorbing ancilla
            if type(boundary_control) == AbsorbingBoundaryControl:
                self.absorption_register = QuantumRegister(1,"absorption")

        if self.absorption_register:
            self.ancilla_registers.append(self.absorption_register)

        
        # initialise coin
        if coin_class == None:
            coin_class = HadamardCoin
        self.n_shift_coin_bits = n_shift_coin_bits if n_shift_coin_bits is not None else math.ceil(math.log2(2*len(system_dimensions)))
        self.shift_coin = coin_class(self.n_shift_coin_bits,**coin_kwargs)

        # initialise Quantum Registers
        self.shift_coin_register = QuantumRegister( self.n_shift_coin_bits,"coin")
        
        # self.state_register = QuantumRegister(self.n_state_bits,"state")
        # self.logic_register = QuantumRegister(self.n_logic_bits,"logic")

        # build quantum circuit
        self.build_ciruit()

        # initialise state
        self.initial_states = initial_states
        self.initialise_states(self.initial_states)
        self.initialise_symetric_coin_register()

        #store results
        self.results = None

    def initialise_states(self, initial_states = None) -> None:
        """initialises the quantum circuit to the values defines in `self.initial_states`"""
        if initial_states is not None:
            assert len(initial_states) == len(self.system_dimensions)

            for idx, n_qubits in enumerate(self.system_dimensions):
                initial_state = initial_states[idx]
                assert len(initial_state) == n_qubits
                for bit_idx, bit in enumerate(initial_state[::-1]):
                    if bit != '0':
                        self.quantum_circuit.x(self.state_registers[idx][bit_idx])

    def initialise_symetric_coin_register(self):
        self.quantum_circuit.u(pi/2,pi/2,3*pi/2,self.shift_coin_register[:])

    def build_ciruit(self) -> None:
        self.quantum_circuit = QuantumCircuit(self.shift_coin_register,*self.ancilla_registers,*self.boundary_control_registers,*self.state_registers)

    def step(self) -> None:
        """Adds one more step to the quantum walk"""
        self.reset_absorption_register()
        self.update_boundary_ancillas()

    def decohere_coin(self, step_idx) -> None:
        """decoheres the coin at selected qubits"""
        if self.coin_decoherence_cycle is None:
            return

        if (step_idx+1)%self.coin_decoherence_cycle.cycle_length == 0:
            for target_idx in self.coin_decoherence_cycle.target_qubits:
                self.quantum_circuit.reset(self.shift_coin_register[target_idx]) 
                self.quantum_circuit.u(pi/2,pi/2,3*pi/2,self.shift_coin_register[target_idx])


    def add_n_steps(self,n_steps) -> None:
        """Adds `n_steps` steps to the quantum walk"""
        for step_idx in range(n_steps):
            self.step()
            self.decohere_coin(step_idx)
    
    def update_boundary_ancillas(self):
        for boundary_control in self.boundary_controls:
            if type(boundary_control) == UniDirectionalBoundaryControl or type(boundary_control)==ControlledDirectionalBoundaryControl:
                boundary_control.reset_ancilla_register(self.quantum_circuit)
                for boundary in boundary_control.boundaries:
                    register = self.state_registers[boundary.dimension]
                    # add one for ancilla
                    n_control_bits = register.size + 1
                    ctrl_state = boundary.bitstring

                    ancilla_register = boundary_control.ancilla_register

                    for ancilla_idx in range(2):
                        # Dreversal gate is just mct. here we apply to the ancilla qubit
                        ancilla_activation_state = ctrl_state + str(ancilla_idx)
                        ancilla_activator = boundary_control.x.control(n_control_bits,ctrl_state=ancilla_activation_state, label = boundary.label)
                        self.quantum_circuit.append(ancilla_activator,[self.shift_coin_register[-1]]+register[:]+[ancilla_register[ancilla_idx]])

            elif type(boundary_control) == NonDisruptiveBoundaryControl or type(boundary_control) == EfficientBoundaryControl:
                boundary_control.reset_ancilla_register(self.quantum_circuit)
                for boundary in boundary_control.boundaries:
                    register = self.state_registers[boundary.dimension]
                    # add one for ancilla
                    n_control_bits = register.size
                    ancilla_activation_state = boundary.bitstring
                    ancilla_register = boundary_control.ancilla_register
                    ancilla_activator = boundary_control.x.control(n_control_bits,ctrl_state=ancilla_activation_state, label = boundary.label)
                    self.quantum_circuit.append(ancilla_activator,register[:]+[ancilla_register[:]])


    def apply_controlled_directional_boundary(self, boundary_control : BoundaryControl):
        ancilla_register = boundary_control.ancilla_register

        # need to refactor this
        n_control_bits = 2
        ctrl_state = "11"
        DReversalGate = self.shift_coin.DReversalGate.control(n_control_bits,ctrl_state=ctrl_state)

        if boundary_control.d_filter:
            Inverse_coin_gate = self.shift_coin.control(1,ctrl_state="1", inverse = True)
        else:
            Inverse_coin_gate = self.shift_coin.control(n_control_bits,ctrl_state=ctrl_state, inverse = True)

        for direction_idx in range(2):
            if boundary_control.d_filter:
                self.quantum_circuit.append(Inverse_coin_gate,[ancilla_register[direction_idx]]+self.shift_coin_register[:])
            else:
                self.quantum_circuit.append(Inverse_coin_gate,[boundary_control.register[direction_idx]]+[ancilla_register[direction_idx]]+self.shift_coin_register[:])

            self.quantum_circuit.append(DReversalGate,[boundary_control.register[direction_idx]]+[ancilla_register[direction_idx]]+self.shift_coin_register[:])


    def apply_unidirectional_boundary(self, boundary_control : BoundaryControl):
        pass
        # for boundary in boundary_control.boundaries:
        #     ancilla_register = boundary_control.ancilla_register

        #     DReversalGate = self.shift_coin.DReversalGate.control(1,ctrl_state="1", label = boundary.label)
        #     Inverse_coin_gate = self.shift_coin.control(1,ctrl_state="1", inverse = True, label = boundary.label)

        #     for direction_idx in range(2):
        #         self.quantum_circuit.append(Inverse_coin_gate,[ancilla_register[direction_idx]]+self.shift_coin_register[:])
        #         self.quantum_circuit.append(DReversalGate,[boundary_control.register[direction_idx]]+[ancilla_register[direction_idx]]+self.shift_coin_register[:])

    def apply_efficient_boundary(self,boundary_control: BoundaryControl):
        ancilla_register = boundary_control.ancilla_register

        ctrl_state = "1" + boundary_control.ctrl_state
        n_control_bits = boundary_control.ctrl_size+1

        DReversalGate = self.shift_coin.DReversalGate.control(n_control_bits,ctrl_state=ctrl_state)
        if boundary_control.d_filter:
            Inverse_coin_gate = self.shift_coin.control(boundary_control.ctrl_size,ctrl_state=boundary_control.ctrl_state, inverse = True)
            self.quantum_circuit.append(Inverse_coin_gate,[ancilla_register[:]]+self.shift_coin_register[:])
        else:
            Inverse_coin_gate = self.shift_coin.control(n_control_bits,ctrl_state="1" + boundary_control.ctrl_state, inverse = True)
            if boundary_control.register:
                self.quantum_circuit.append(Inverse_coin_gate,[boundary_control.register[:]]+[ancilla_register[:]]+self.shift_coin_register[:])
            else:
                self.quantum_circuit.append(Inverse_coin_gate,[ancilla_register[:]]+self.shift_coin_register[:])
        if boundary_control.register:
            self.quantum_circuit.append(DReversalGate,[boundary_control.register[:]]+[ancilla_register[:]]+self.shift_coin_register[:])
        else:
            self.quantum_circuit.append(DReversalGate,[ancilla_register[:]]+self.shift_coin_register[:])


    def apply_non_disruptive_boundary_cleanup(self):
        for boundary_control in self.boundary_controls:
            if type(boundary_control) == NonDisruptiveBoundaryControl:
                ancilla_register = boundary_control.ancilla_register

                ctrl_state = "1" + boundary_control.ctrl_state
                n_control_bits = boundary_control.ctrl_size+1

                    # DReversalGate = self.shift_coin.DReversalGate.control(n_control_bits,ctrl_state=ctrl_state , label = boundary.label)
                    # self.quantum_circuit.append(DReversalGate,[boundary_control.register[:]]+[ancilla_register[:]]+self.shift_coin_register[:])


                if boundary_control.d_filter:
                    Inverse_coin_gate = self.shift_coin.control(boundary_control.ctrl_size,ctrl_state=boundary_control.ctrl_state, inverse = False)
                    self.quantum_circuit.append(Inverse_coin_gate,[ancilla_register[:]]+self.shift_coin_register[:])
                else:
                    Inverse_coin_gate = self.shift_coin.control(n_control_bits,ctrl_state="1" + boundary_control.ctrl_state, inverse = False)
                    if boundary_control.register:
                        self.quantum_circuit.append(Inverse_coin_gate,[boundary_control.register[:]]+[ancilla_register[:]]+self.shift_coin_register[:])
                    else:
                        self.quantum_circuit.append(Inverse_coin_gate,[ancilla_register[:]]+self.shift_coin_register[:])

                  

    def apply_boundary(self,boundary_control : BoundaryControl):
        """Applys boundary condition to environment specified by `boundary`"""
        if (type(boundary_control)==ControlledDirectionalBoundaryControl):
            return self.apply_controlled_directional_boundary(boundary_control)
            
        if type(boundary_control) == UniDirectionalBoundaryControl:
            return self.apply_unidirectional_boundary(boundary_control)

        if type(boundary_control)==NonDisruptiveBoundaryControl or type(boundary_control)==EfficientBoundaryControl:
            return self.apply_efficient_boundary(boundary_control)


        for boundary in boundary_control.boundaries:


            if type(boundary)==Obstruction:
                registers = [self.state_registers[dim] for dim in boundary.dimensions]
                n_control_bits = sum([reg.size for reg in registers]) + boundary_control.ctrl_size
                ctrl_state = "".join(boundary.bitstrings) + boundary_control.ctrl_state
                DReversalGate = self.shift_coin.DReversalGate.control(n_control_bits,ctrl_state=ctrl_state, label = boundary.label)
                Inverse_coin_gate = self.shift_coin.control(n_control_bits,ctrl_state=ctrl_state, inverse = True, label = boundary.label)

                state_qubits = []
                for reg in registers:
                    state_qubits.extend(reg[:])

                if boundary_control.register:
                    self.quantum_circuit.append(Inverse_coin_gate,boundary_control.register[:]+state_qubits+self.shift_coin_register[:])
                    self.quantum_circuit.append(DReversalGate,boundary_control.register[:]+state_qubits+self.shift_coin_register[:])

                else:  
                    self.quantum_circuit.append(Inverse_coin_gate,state_qubits+self.shift_coin_register[:])
                    self.quantum_circuit.append(DReversalGate,state_qubits+self.shift_coin_register[:])
                
                continue


            register = self.state_registers[boundary.dimension]
            n_control_bits = register.size + boundary_control.ctrl_size
            ctrl_state = boundary.bitstring + boundary_control.ctrl_state

            # construct boundary logic
            DReversalGate = self.shift_coin.DReversalGate.control(n_control_bits,ctrl_state=ctrl_state, label = boundary.label)

            if boundary_control.d_filter:
                Inverse_coin_gate = self.shift_coin.control(register.size,ctrl_state=boundary.bitstring, inverse = True, label = boundary.label)
            else:
                Inverse_coin_gate = self.shift_coin.control(n_control_bits,ctrl_state=ctrl_state, inverse = True, label = boundary.label)
                


            if type(boundary_control) == AbsorbingBoundaryControl:

                n_control_bits = register.size
                ctrl_state = boundary.bitstring
                AbsorptionControlGate = boundary_control.ctrl.control(n_control_bits,ctrl_state=ctrl_state,label = boundary.label)
                self.quantum_circuit.append(AbsorptionControlGate,register[:]+self.absorption_register[:])

            elif boundary_control.register:
                if boundary_control.d_filter:
                    self.quantum_circuit.append(Inverse_coin_gate,register[:]+self.shift_coin_register[:])
                else:
                    self.quantum_circuit.append(Inverse_coin_gate,boundary_control.register[:]+register[:]+self.shift_coin_register[:])
                self.quantum_circuit.append(DReversalGate,boundary_control.register[:]+register[:]+self.shift_coin_register[:])

            else:
                self.quantum_circuit.append(Inverse_coin_gate,register[:]+self.shift_coin_register[:])
                self.quantum_circuit.append(DReversalGate,register[:]+self.shift_coin_register[:])


        self.quantum_circuit.barrier()
    
    
    def add_shift_coin(self):
        """Adds a coin operator to the coin register"""
        self.quantum_circuit.append(self.shift_coin.gate,self.shift_coin_register[:])
    
    def add_boundary_coins(self):
        """Adds boundary control coins"""
        for boundary_control in self.boundary_controls:
            if boundary_control.ctrl and type(boundary_control.ctrl) != CylicController and type(boundary_control.ctrl) != AbsorbingControl:
                boundary_ctrl = boundary_control.ctrl.gate
                self.quantum_circuit.append(boundary_ctrl,boundary_control.register[:])
    
    def add_coins(self):
        self.add_shift_coin()
        self.add_boundary_coins()
        self.quantum_circuit.barrier()

    def reset_boundaries(self):
        for boundary in self.boundary_controls:
            boundary.reset_register(self.quantum_circuit)

    def apply_post_shift_operations(self):
        self.apply_non_disruptive_boundary_cleanup()




    def reset_absorption_register(self):
        if self.absorption_register is None:
            return None
        self.quantum_circuit.reset(self.absorption_register[:])
        self.quantum_circuit.x(self.absorption_register[:])


        
    def add_left_shift(self,dimension):
        """Performs the left shift (-1) operator on the target register specified by its `dimension`"""
        register = self.state_registers[dimension]
        n_register_bits = register.size
        # Apply sequential CX gates
        for idx in range(n_register_bits):
            if self.absorption_register:
                self.quantum_circuit.mct(self.shift_coin_register[:]+self.absorption_register[:]+register[:idx],register[idx])
            else:
                self.quantum_circuit.mct(self.shift_coin_register[:]+register[:idx],register[idx])

            
        # readability barrier
        self.quantum_circuit.barrier()

    def add_right_shift(self,dimension):
        """Performs the right shift (+1) operator on the target register specified by it's `dimension`"""
        register = self.state_registers[dimension]
        n_register_bits = register.size
        # Apply sequential CX gates
        for idx in range(n_register_bits)[::-1]:
            if self.absorption_register:
                self.quantum_circuit.mct(self.shift_coin_register[:]+self.absorption_register[:]+register[:idx],register[idx])
            else:
                self.quantum_circuit.mct(self.shift_coin_register[:]+register[:idx],register[idx])
        # readability barrier
        self.quantum_circuit.barrier()

    def wrap_shift(self,operator,coin_bitstring,dimension):
        """Wraps an operator to execute for a particular coin bitstring"""
        bit_indices = [i for i in range(len(coin_bitstring))]

        for idx,bit in zip(bit_indices[::-1],coin_bitstring):
            if bit == '0':
                self.quantum_circuit.x(self.shift_coin_register[idx])

        operator(dimension)

        for idx,bit in zip(bit_indices[::-1],coin_bitstring):
            if bit == '0':
                self.quantum_circuit.x(self.shift_coin_register[idx])

        self.quantum_circuit.barrier()

    def get_state_register_indices(self)-> list:
        """Returns a list of dictionaries decsribing the start and end qubits of each state register"""
        indices = []
        last_idx = 0

        for idx, dimension_len in enumerate (self.system_dimensions[::-1]):
            dimension_start_idx = sum(self.system_dimensions[:idx])
            dimension_end_idx = dimension_start_idx + dimension_len - 1
            indices.append({
                "dimension" : idx,
                "start_idx": dimension_start_idx,
                "end_idx": dimension_end_idx})

            last_idx = dimension_end_idx

        return indices, last_idx

    def discard_non_state_bits(self,counts : dict, inplace = False) -> dict:
        """discards the non state bits from a sim run and recreates the `counts` dictionary"""
        _ , last_state_idx = self.get_state_register_indices()
        
        counts_new = {}
        
        for bitstring, count in counts.items():
            state_bitstring = bitstring[:last_state_idx+1]
            if counts_new.get(state_bitstring):
                counts_new[state_bitstring] += count

            else:
                counts_new[state_bitstring] = count

        if inplace:
            counts = counts_new
        
        return counts_new


    def load_results_from_IBM(self, job_id: str, return_elapsed_time = False):
        """Processes results from an IBM job_id"""
        job = self.load_job_from_IBM(job_id)
        queue_position = job.queue_position()
        assert job.done(), "Job in position {} in the queue, try again later".format(queue_position)
        return self.get_results(job, return_elapsed_time)

    def process_counts(self,counts,shots):
        """Processes raw count data from qiskit into data relating to physical space"""
        state_register_indices, _ = self.get_state_register_indices()
        displacement_tensors = {}
        for idx in range(self.n_system_dimensions):
            displacement_tensors["dimension_{}".format(idx)] = []
        
        displacement_tensors["probability_density"] = []
        for key, value in counts.items():
            for dimension_params in state_register_indices:
                dimensional_displacement = int(key[dimension_params['start_idx']:1+dimension_params['end_idx']], 2)
                displacement_tensors["dimension_{}".format(dimension_params["dimension"])].append(dimensional_displacement)

            displacement_tensors["probability_density"].append(1.0*value/shots)


        self.results = displacement_tensors
        return displacement_tensors

    def get_results(self,job, return_elapsed_time = False) -> dict:
        """processes results from a Qiskit job"""

        results = job.result()
        counts = results.get_counts()
        counts = self.discard_non_state_bits(counts, False)
        shots = results.results[0].shots
        displacement_tensors = self.process_counts(counts=counts, shots=shots)
        return (displacement_tensors, results.time_taken) if return_elapsed_time else displacement_tensors

    def run_experiment(self,n_steps,shots = 1024, initial_states = None):
        """runs a quantum walk of `n_steps` """
        # reset_circuit
        self.reset_circuit(initial_states)

        # add n_steps
        self.add_n_steps(n_steps=n_steps)

        # if on IBM submit job
        if self.backend.is_on_IBM:
            return self._submit_job_on_IBM(shots)

        return self.run_job_locally(shots)

    @staticmethod
    def merge_counts(total_counts, counts_appendage):
        """Merge two count dictionaries"""
 
        for bitstring, n_shots in counts_appendage.items():
            if total_counts.get(bitstring) is None:
                total_counts[bitstring] = 0
            total_counts[bitstring]+=n_shots

    def run_decoherence_experiment(self,n_steps: int,decoherence_intervals: int, shots=1024,initial_states = None, return_elapsed_time=False):
        """Runs a decoherence experiment"""
        state_register_indices, _ = self.get_state_register_indices()

        n_full_cycles = n_steps//decoherence_intervals
        remainder_steps = n_steps%decoherence_intervals

        # initialise counts to n_shots at initial position
        counts = self.run_experiment(n_steps=0,shots=shots,initial_states=initial_states).result().get_counts()
        counts = self.discard_non_state_bits(counts, False)

        total_time = 0
        # full cycles
        for cycle in range(n_full_cycles):
            total_counts = {}
            print(f"decohenerence cycle {cycle+1}")
            for bitstring, n_shots in counts.items():
                initial_states = []
                for dimension_params in state_register_indices:
                        initial_states.append(bitstring[dimension_params['start_idx']:1+dimension_params['end_idx']])
                job = self.run_experiment(n_steps = decoherence_intervals, shots=n_shots, initial_states=initial_states)
                results = job.result()
                counts_appendage = results.get_counts()
                counts_appendage = self.discard_non_state_bits(counts_appendage, False)
                self.merge_counts(total_counts=total_counts,counts_appendage=counts_appendage)
                total_time+=results.time_taken

            counts = total_counts


        # remainder cyle
        if remainder_steps:
            print(f"decohenerence cycle {n_full_cycles+1}")
            total_counts = {}
            for bitstring, n_shots in counts.items():
                initial_states = []
                for dimension_params in state_register_indices:
                        initial_states.append(bitstring[dimension_params['start_idx']:1+dimension_params['end_idx']])
                job = self.run_experiment(n_steps = remainder_steps, shots=n_shots, initial_states=initial_states)
                results = job.result()
                counts_appendage = results.get_counts()
                counts_appendage = self.discard_non_state_bits(counts_appendage, False)
                self.merge_counts(total_counts=total_counts,counts_appendage=counts_appendage)
                total_time+=results.time_taken

            counts = total_counts

        displacement_tensors = self.process_counts(counts=counts, shots=shots)
        return (displacement_tensors, total_time) if return_elapsed_time else displacement_tensors

    def run_job_locally(self, shots = 1024):
        """Runs a simulation of the quantum circuit for the number of shits specified by `shots`"""
        quantum_circuit_copy = self.quantum_circuit.copy()
        quantum_circuit_copy.measure_all()
        transpiled_circuit = transpile(quantum_circuit_copy, self.backend.backend)
        qobj = assemble(transpiled_circuit,shots = shots)
        job = self.backend.backend.run(qobj)
        return job

    def _submit_job_on_IBM(self, shots = 1024):
        """Runs a simulation of the quantum circuit for the number of shits specified by `shots` on IBM hardware"""
        quantum_circuit_copy = self.quantum_circuit.copy()
        quantum_circuit_copy.measure_all()
        transpiled_circuit = transpile(quantum_circuit_copy, self.backend.backend)
        qobj = assemble(transpiled_circuit,backend = self.backend.backend, shots = shots)
        job = self.backend.backend.run(qobj)
        print("JOB_ID: {}".format(job.job_id()))
        return job

    def load_job_from_IBM(self,job_id: str):
        """Retrieves a completed job run on IBM hardware"""
        job = self.backend.backend.retrieve_job(job_id)
        return job






    def draw_circuit(self,savepath) -> None:
        """draws the circuit and saves the image to the path passed into `savepath`"""
        style = {'dpi' : 250}
        circuit_drawer(self.quantum_circuit, output='mpl',filename=savepath, style = style)

    def draw_debug(self,savepath):
        self.reset_circuit()
        self.step()
        self.quantum_circuit.measure_all()
        self.draw_circuit(savepath)
        self.reset_circuit()
      

    def reset_circuit(self, initial_states = None):
        """clears the circuit and initialises to its initial states"""
        if initial_states is None:
            initial_states = self.initial_states
        self.build_ciruit()
        self.initialise_states(initial_states)
        self.initialise_symetric_coin_register()
        




    def get_covariance_tensor(self,force_rerun = False):
        """returns the covariance tensor of the quantum walk"""
        if self.results is None or force_rerun:
            job = self.run_job_locally()
            self.get_results(job)

        dimension_displacements = {}
        for key, value in self.results.items():
            if key == "probability_density":
                continue
            dim = "d"+str(key)[-1]
            dimension_displacements[dim] = value

        dimension_displacements = pd.DataFrame(dimension_displacements)
        return dimension_displacements.corr()


        

        

class QuantumWalk3D(QuantumWalk):
    def __init__(self,backend: Backend, system_dimensions: list, initial_states: list = None, n_shift_coin_bits: int = None, coin_class=None, coin_kwargs = {}, boundary_controls = [], coin_decoherence_cycle: CoinDecoherenceCycle = None) -> None:
        assert len(system_dimensions) == 3
        super().__init__(backend,system_dimensions, initial_states, n_shift_coin_bits, coin_class, coin_kwargs, boundary_controls, coin_decoherence_cycle)

    def step(self) -> None:
        super().step()
        self.add_coins()
        for boundary in self.boundary_controls:
            self.apply_boundary(boundary)
        # dimension 0
        self.wrap_shift(operator = self.add_left_shift,coin_bitstring = "100",dimension=0)
        self.wrap_shift(operator = self.add_right_shift,coin_bitstring = "000",dimension=0)
        # dimension 1
        self.wrap_shift(operator = self.add_left_shift,coin_bitstring = "101",dimension=1)
        self.wrap_shift(operator = self.add_right_shift,coin_bitstring = "001",dimension=1)
        # dimension 2
        self.wrap_shift(operator = self.add_left_shift,coin_bitstring = "110",dimension=2)
        self.wrap_shift(operator = self.add_right_shift,coin_bitstring = "010",dimension=2)
        self.apply_post_shift_operations()
        self.reset_boundaries()

class QuantumWalk2D(QuantumWalk):
    def __init__(self,backend: Backend, system_dimensions: list, initial_states: list = None, n_shift_coin_bits: int = None, coin_class=None, coin_kwargs = {}, boundary_controls = [], coin_decoherence_cycle: CoinDecoherenceCycle = None) -> None:
        assert len(system_dimensions) == 2
        super().__init__(backend,system_dimensions, initial_states, n_shift_coin_bits, coin_class, coin_kwargs, boundary_controls, coin_decoherence_cycle)

    def step(self) -> None:
        super().step()
        self.add_coins()
        for boundary in self.boundary_controls:
            self.apply_boundary(boundary)
        # dimension 0
        self.wrap_shift(operator = self.add_left_shift,coin_bitstring = "10",dimension=0)
        self.wrap_shift(operator = self.add_right_shift,coin_bitstring = "00",dimension=0)
        # dimension 1
        self.wrap_shift(operator = self.add_left_shift,coin_bitstring = "11",dimension=1)
        self.wrap_shift(operator = self.add_right_shift,coin_bitstring = "01",dimension=1)
        self.apply_post_shift_operations()
        self.reset_boundaries()

    def initialise_symetric_coin_register(self):
        self.quantum_circuit.u(pi/2,pi/2,3*pi/2,self.shift_coin_register[0])
        self.quantum_circuit.u(pi/2,3*pi/2,pi/2,self.shift_coin_register[1])


class QuantumWalk1D(QuantumWalk):
    def __init__(self,backend: Backend, system_dimensions: int, initial_states: str = None, n_shift_coin_bits: int = None, coin_class=None ,coin_kwargs = {}, boundary_controls = [], coin_decoherence_cycle: CoinDecoherenceCycle = None) -> None:
        if type(system_dimensions) == int:
            system_dimensions = [system_dimensions]
        if initial_states is not None and type(initial_states) == str:
            initial_states = [initial_states]
        super().__init__(backend,system_dimensions, initial_states, n_shift_coin_bits, coin_class, coin_kwargs, boundary_controls, coin_decoherence_cycle)


    def step(self) -> None:
        super().step()
        self.add_coins()
        for boundary in self.boundary_controls:
            self.apply_boundary(boundary)
        # dimension 0
        self.wrap_shift(operator = self.add_left_shift,coin_bitstring = "1",dimension=0)
        self.wrap_shift(operator = self.add_right_shift,coin_bitstring = "0",dimension=0)
        self.apply_post_shift_operations()
        self.reset_boundaries()

class QuantumWalk2DIndependant(QuantumWalk):

    def __init__(self,backend: Backend, system_dimensions: list, initial_states: list = None, n_shift_coin_bits: int = None, coin_class=None, coin_kwargs = {}, boundary_controls = [], coin_decoherence_cycle: CoinDecoherenceCycle = None) -> None:
        assert len(system_dimensions) == 2
        super().__init__(backend,system_dimensions, initial_states, n_shift_coin_bits, coin_class, coin_kwargs, boundary_controls, coin_decoherence_cycle)

    def step(self) -> None:
        super().step()
        self.add_coins()
        for boundary in self.boundary_controls:
            self.apply_boundary(boundary)
        # dimension 0
        self.wrap_shift(operator = self.add_left_shift,coin_bitstring = "10",dimension=0)
        self.wrap_shift(operator = self.add_left_shift,coin_bitstring = "11",dimension=0)
        self.wrap_shift(operator = self.add_right_shift,coin_bitstring = "01",dimension=0)
        self.wrap_shift(operator = self.add_right_shift,coin_bitstring = "00",dimension=0)
        # dimension 1
        self.wrap_shift(operator = self.add_left_shift,coin_bitstring = "00",dimension=1)
        self.wrap_shift(operator = self.add_left_shift,coin_bitstring = "10",dimension=1)
        self.wrap_shift(operator = self.add_right_shift,coin_bitstring = "11",dimension=1)
        self.wrap_shift(operator = self.add_right_shift,coin_bitstring = "01",dimension=1)
        self.apply_post_shift_operations()
        self.reset_boundaries()