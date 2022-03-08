

from fileinput import filename
import math
from qiskit import Aer, QuantumCircuit, QuantumRegister, transpile, assemble
from qiskit.tools.visualization import circuit_drawer
from qiskit.providers.aer import AerError
import pandas as pd
from DiffusionProject.Algorithms.Coins import HadamardCoin, CylicController
from DiffusionProject.Algorithms.Boundaries import Boundary, OneWayBoundary

class Backend:
    """wrapper for Qiskit sim backend """
    def __init__(self,use_GPU = False) -> None:
        self.__simulator = Aer.get_backend('aer_simulator')
        self.__device = "CPU"
        # init GPU backend
        if use_GPU:
            try:
                self.__simulator.set_options(device='GPU')
                self.__device = "GPU"
            except AerError as e:
                print(e)

        print("running on device: {}".format(self.__device))

    @property
    def simulator(self):
        return self.__simulator

    @property
    def device(self):
        return self.__device
        
class QuantumWalk:

    def __init__(self,backend: Backend ,system_dimensions: list, initial_states: list = None, n_shift_coin_bits: int = None, coin_class = None, boundaries = [] ) -> None:
        """
        Create a new `QuantumWalk` Object
        Args:
            backend (`DiffusionProject.Algorithms.Walks.Backend`): The Qiskit backend to run the simulation on\n
            system_dimensions ([int]): a list of the number of qubits used to represent each succesive dimension. e.g for a 2qubitx3qubit system pass in [2,3]\n
            initial_states ([str]) a list of bitsrings to represent the initial state of the system. e.g ["100","110"]. If no arguments are passed the system will start in all 0 states

        
        """

        # qiskit sim backend
        self.backend = backend

        # initialise dimensional states:
        self.state_registers = []
        self.system_dimensions = system_dimensions
        self.n_system_dimensions = len(self.system_dimensions)

        for idx, n_qubits in enumerate(system_dimensions):
            register_name = "dimension{}".format(idx)
            self.state_registers.append(QuantumRegister(n_qubits,register_name))

        # initialise boundary control registers:
        self.boundaries = boundaries
        self.boundary_control_registers = []
        for boundary in self.boundaries:
            assert boundary.dimension >= 0 and boundary.dimension < len(self.system_dimensions)
            assert boundary.n_bits == self.system_dimensions[boundary.dimension]
            if boundary.ctrl is not None or type(boundary) == OneWayBoundary:
                self.boundary_control_registers.append(boundary.register)
        
        # initialise coin
        if coin_class == None:
            coin_class = HadamardCoin
        self.n_shift_coin_bits = n_shift_coin_bits if n_shift_coin_bits is not None else math.ceil(math.log2(2*len(system_dimensions)))
        self.shift_coin = coin_class(self.n_shift_coin_bits)

        # initialise Quantum Registers
        self.shift_coin_register = QuantumRegister( self.n_shift_coin_bits,"coin")
        # self.state_register = QuantumRegister(self.n_state_bits,"state")
        # self.logic_register = QuantumRegister(self.n_logic_bits,"logic")

        # build quantum circuit
        self.build_ciruit()

        # initialise state
        self.initial_states = initial_states
        self.initialise_states()

        #store results
        self.results = None

    def initialise_states(self) -> None:
        """initialises the quantum circuit to the values defines in `self.initial_states`"""
        if self.initial_states is not None:
            assert len(self.initial_states) == len(self.system_dimensions)

            for idx, n_qubits in enumerate(self.system_dimensions):
                initial_state = self.initial_states[idx]
                assert len(initial_state) == n_qubits
                for bit_idx, bit in enumerate(initial_state[::-1]):
                    if bit != '0':
                        self.quantum_circuit.x(self.state_registers[idx][bit_idx])

    def build_ciruit(self) -> None:
        self.quantum_circuit = QuantumCircuit(self.shift_coin_register,*self.boundary_control_registers,*self.state_registers)

    def step(self) -> None:
        """Adds one more step to the quantum walk"""
        pass

    def add_n_steps(self,n_steps) -> None:
        """Adds `n_steps` steps to the quantum walk"""
        for _ in range(n_steps):
            self.step()

    def apply_boundary(self,boundary : Boundary):
        """Applys boundary condition to environment specified by `boundary`"""

        register = self.state_registers[boundary.dimension]
        n_control_bits = register.size + boundary.ctrl_size
        ctrl_state = boundary.bitstring + boundary.ctrl_state

        # construct boundary logic
        DReversalGate = self.shift_coin.DReversalGate.control(n_control_bits,ctrl_state=ctrl_state, label = boundary.label)
        Inverse_coin_gate = self.shift_coin.control(n_control_bits,ctrl_state=ctrl_state, inverse = True, label = boundary.label)

        if type(boundary) == OneWayBoundary:
            n_control_bits = register.size
            ctrl_state = boundary.bitstring
            Inverse_coin_gate = self.shift_coin.control(n_control_bits,ctrl_state=ctrl_state, inverse = True, label = boundary.label)
            
            DRestorationGate = self.shift_coin.DReversalGate.control(n_control_bits,ctrl_state=ctrl_state, label = boundary.label)
            CyclicControlGate = boundary.ctrl.control(n_control_bits,ctrl_state=ctrl_state,label = boundary.label)
            
            
            self.quantum_circuit.append(Inverse_coin_gate,register[:]+self.shift_coin_register[:])
            
            self.quantum_circuit.append(CyclicControlGate,register[:]+boundary.register[:])
            self.quantum_circuit.append(DRestorationGate,register[:]+self.shift_coin_register[:])
            
            self.quantum_circuit.append(DReversalGate,boundary.register[:]+register[:]+self.shift_coin_register[:])
            

        
   
        elif boundary.register:
            self.quantum_circuit.append(Inverse_coin_gate,boundary.register[:]+register[:]+self.shift_coin_register[:])
            self.quantum_circuit.append(DReversalGate,boundary.register[:]+register[:]+self.shift_coin_register[:])

        else:
            self.quantum_circuit.append(Inverse_coin_gate,register[:]+self.shift_coin_register[:])
            self.quantum_circuit.append(DReversalGate,register[:]+self.shift_coin_register[:])


        self.quantum_circuit.barrier()
    
    
    def add_shift_coin(self):
        """Adds a coin operator to the coin register"""
        self.quantum_circuit.append(self.shift_coin.gate,self.shift_coin_register[:])
    
    def add_boundary_coins(self):
        """Adds boundary control coins"""
        for boundary in self.boundaries:
            if boundary.ctrl and type(boundary.ctrl) != CylicController:
                boundary_ctrl = boundary.ctrl.gate
                self.quantum_circuit.append(boundary_ctrl,boundary.register[:])
    
    def add_coins(self):
        self.add_shift_coin()
        self.add_boundary_coins()
        self.quantum_circuit.barrier()

    def reset_boundaries(self):
        for boundary in self.boundaries:
            boundary.reset_register(self.quantum_circuit)

        
    def add_left_shift(self,dimension):
        """Performs the left shift (-1) operator on the target register specified by its `dimension`"""
        register = self.state_registers[dimension]
        n_register_bits = register.size
        # Apply sequential CX gates
        for idx in range(n_register_bits):
            self.quantum_circuit.mct(self.shift_coin_register[:]+register[:idx],register[idx])
        # readability barrier
        self.quantum_circuit.barrier()

    def add_right_shift(self,dimension):
        """Performs the right shift (+1) operator on the target register specified by it's `dimension`"""
        register = self.state_registers[dimension]
        n_register_bits = register.size
        # Apply sequential CX gates
        for idx in range(n_register_bits)[::-1]:
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

        for idx, dimension_len in enumerate (self.system_dimensions):
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

    def get_results(self, shots = 1024, return_counts = False) -> dict:
        """Runs a simulation of the quantum circuit for the number of shits specified by `shots`"""
        state_register_indices, _ = self.get_state_register_indices()

        quantum_circuit_copy = self.quantum_circuit.copy()
        quantum_circuit_copy.measure_all()
        transpiled_circuit = transpile(quantum_circuit_copy, self.backend.simulator)
        qobj = assemble(transpiled_circuit,shots = shots)
        results = self.backend.simulator.run(qobj).result()
        counts = results.get_counts()
        counts = self.discard_non_state_bits(counts, False)


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
        return (displacement_tensors, counts) if return_counts else displacement_tensors

    def run_experiment(self,n_steps,shots = 1024):
        """runs a quantum walk of `n_steps` """

        # reset_circuit
        self.reset_circuit()

        # add n_steps
        self.add_n_steps(n_steps=n_steps)
        return self.get_results(shots=shots)

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
      

    def reset_circuit(self):
        """clears the circuit and initialises to its initial states"""
        self.build_ciruit()
        self.initialise_states()
        




    def get_covariance_tensor(self,force_rerun = False):
        """returns the covariance tensor of the quantum walk"""
        if self.results is None or force_rerun:
            self.get_results()

        dimension_displacements = {}
        for key, value in self.results.items():
            if key == "probability_density":
                continue
            dim = "d"+str(key)[-1]
            dimension_displacements[dim] = value

        dimension_displacements = pd.DataFrame(dimension_displacements)
        return dimension_displacements.corr()


        

        

class QuantumWalk3D(QuantumWalk):
    def __init__(self,backend: Backend, system_dimensions: list, initial_states: list = None, n_shift_coin_bits: int = None, coin_class=None, boundaries=[]) -> None:
        assert len(system_dimensions) == 3
        super().__init__(backend,system_dimensions, initial_states, n_shift_coin_bits, coin_class, boundaries)

    def step(self) -> None:
        self.add_coins()
        for boundary in self.boundaries:
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
        self.reset_boundaries()

class QuantumWalk2D(QuantumWalk):
    def __init__(self,backend: Backend, system_dimensions: list, initial_states: list = None, n_shift_coin_bits: int = None, coin_class=None, boundaries=[]) -> None:
        assert len(system_dimensions) == 2
        super().__init__(backend,system_dimensions, initial_states, n_shift_coin_bits, coin_class, boundaries)

    def step(self) -> None:
        self.add_coins()
        for boundary in self.boundaries:
            self.apply_boundary(boundary)
        # dimension 0
        self.wrap_shift(operator = self.add_left_shift,coin_bitstring = "10",dimension=0)
        self.wrap_shift(operator = self.add_right_shift,coin_bitstring = "00",dimension=0)
        # dimension 1
        self.wrap_shift(operator = self.add_left_shift,coin_bitstring = "11",dimension=1)
        self.wrap_shift(operator = self.add_right_shift,coin_bitstring = "01",dimension=1)
        self.reset_boundaries()


class QuantumWalk1D(QuantumWalk):
    def __init__(self,backend: Backend, system_dimensions: int, initial_states: str = None, n_shift_coin_bits: int = None, coin_class=None, boundaries=[]) -> None:
        assert type(system_dimensions) == int
        if initial_states is not None:
            initial_states = [initial_states]
        super().__init__(backend,[system_dimensions], initial_states, n_shift_coin_bits, coin_class, boundaries)


    def step(self) -> None:
        self.add_coins()
        for boundary in self.boundaries:
            self.apply_boundary(boundary)
        # dimension 0
        self.wrap_shift(operator = self.add_left_shift,coin_bitstring = "1",dimension=0)
        self.wrap_shift(operator = self.add_right_shift,coin_bitstring = "0",dimension=0)
        self.reset_boundaries()
