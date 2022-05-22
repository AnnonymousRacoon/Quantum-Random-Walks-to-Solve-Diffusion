import numpy as np
from qiskit import QuantumRegister, QuantumCircuit
from DiffusionProject.Algorithms.Coins import Coin, SU2Coin
from DiffusionProject.Algorithms.Coins import AbsorbingControl

class Obstruction:
    """Represents a single obstructive point in  lattice"""

    def __init__(self, bitstrings: list, dimensions:list, label=None) -> None:
        assert len(bitstrings)==len(dimensions), "The number of bitstrings must equal the number of dimensions"
        self._bitstrings = bitstrings
        self._dimensions = dimensions
        self._label = label

    @property
    def n_bits(self) -> list:
        """The length of the boundary bitstring"""
        return [len(bitstring) for bitstring in self._bitstrings]

    @property
    def dimensions(self) -> list:
        return self._dimensions

    @property
    def bitstrings(self)-> list:
        return self._bitstrings

    @property
    def label(self) -> str:
        return self._label
        
class Boundary:
    """Represents a single boundary plane in a quantum walk algorithm"""

    def __init__(self,bitstring: str, dimension = 0, label = None) -> None:
        """ """
        self._bitstring = bitstring
        self._dimension = dimension
        self._label = label
            
    @property
    def n_bits(self) -> int:
        """The length of the boundary bitstring"""
        return len(self._bitstring)

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def bitstring(self)-> str:
        return self._bitstring

    @property
    def label(self) -> str:
        return self._label




class BoundaryControl:
    """
    Controls One or More Boundaries
    """
    
    def __init__(self, ctrl: Coin = None, ctrl_state = None, n_resets = 2, label = None, d_filter = False) -> None:

        self._d_filter = d_filter
        self._boundaries = []
        self._n_resets = n_resets
        self._ctrl = ctrl
        self._label = label
        self._ancilla_register = None

        if ctrl is not None:
            self._ctrl_size = ctrl.n_qubits
            register_name = "{} control".format(label)
            self._register = QuantumRegister(self._ctrl_size,register_name) if label else QuantumRegister(self._ctrl_size, "boundary control") 
        else:
            self._ctrl_size = 0
            self._register = None

        

        if ctrl is None:
            self._ctrl_state = ""

        elif ctrl is not None and ctrl_state is None:
            self._ctrl_state = "1"*ctrl.n_qubits


        elif ctrl_state != None:
            assert ctrl is not None
            assert len(ctrl_state) == ctrl.n_qubits
            self._ctrl_state = ctrl_state 
        
    def add_boundary(self,boundary: Boundary):
        self._boundaries.append(boundary)

    def add_boundaries(self, boundaries: list):
        for boundary in boundaries:
            self.add_boundary(boundary)

    def reset_register(self,circuit):
        for qubit_idx in range(self._ctrl_size):
            for _ in range(self._n_resets):
                circuit.reset(self._register[qubit_idx])

    def reset_ancilla_register(self,circuit):
        for qubit_idx in range(self._ancilla_register.size):
            for _ in range(self._n_resets):
                circuit.reset(self._ancilla_register[qubit_idx])

    @property
    def boundaries(self):
        return self._boundaries[:]

    @property
    def ctrl(self) -> Coin:
        return self._ctrl

    @property
    def register(self) -> QuantumRegister:
        return self._register

    @property
    def ancilla_register(self) -> QuantumRegister:
        return self._ancilla_register

    @property
    def ctrl_state(self) -> str:
        return self._ctrl_state

    @property
    def ctrl_size(self) -> int:
        return self._ctrl_size

    @property
    def label(self):
        return self._label

    @property
    def is_permeable(self):
        return self._ctrl != None

    @property
    def d_filter(self):
        return self._d_filter

    @property
    def x(self):
        qc = QuantumCircuit(1)
        qc.x(-1)
        directional_reversal_gate = qc.to_gate(label = "mct")
        return directional_reversal_gate

class ControlledDirectionalBoundaryControl(BoundaryControl):
    def __init__(self, ctrl: Coin = None, probabilities = None, ctrl_state=None, n_resets=2, label=None, d_filter = False) -> None:
        if ctrl is None:
            assert type(probabilities) == list and len(probabilities) == 2
            assert not any([p <0 and p>1 for p in probabilities])
            thetas = [np.arccos(p**0.5) for p in probabilities]
            ctrl = SU2Coin(2,thetas,0,0)
        else:
            assert ctrl != None
            assert ctrl.n_qubits == 2, "Control coin must have two qubits"
        super().__init__(ctrl, ctrl_state, n_resets, label, d_filter)
        self._ancilla_register = QuantumRegister(2,"directional ancilla")


class UniDirectionalBoundaryControl(BoundaryControl):
    def __init__(self, direction: str, ctrl: Coin, ctrl_state=None, n_resets=2, label=None,  d_filter=False) -> None:
        ctrl = None
        assert direction.lower() in ["left","right",'l',"r"]
        self._direction = direction
        self._ancilla_idx = 0 if direction[0] == "r" else 1
        super().__init__(ctrl, ctrl_state, n_resets, label, d_filter)
        self._ancilla_register = QuantumRegister(2,"directional ancilla")

    @property
    def ancilla_idx(self):
        return self._ancilla_idx



class NonDisruptiveBoundaryControl(BoundaryControl):
    def __init__(self, ctrl: Coin = None, ctrl_state=None, n_resets=2, label=None, d_filter=False) -> None:
        super().__init__(ctrl, ctrl_state, n_resets, label, d_filter)
        self._ancilla_register = QuantumRegister(1,"ndbc ancilla")



class AbsorbingBoundaryControl(BoundaryControl):
    def __init__(self, ctrl_state=None, n_resets=2, label=None) -> None:
        ctrl = AbsorbingControl()
        super().__init__(ctrl, ctrl_state, n_resets, label)

    def reset_register(self,circuit):
        pass




