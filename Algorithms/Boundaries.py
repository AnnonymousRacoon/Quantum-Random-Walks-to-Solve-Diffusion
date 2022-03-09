from qiskit import QuantumRegister
from DiffusionProject.Algorithms.Coins import Coin, CylicController

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
    
    def __init__(self, ctrl: Coin = None, ctrl_state = None, n_resets = 2, label = None) -> None:

        self._boundaries = []
        self._n_resets = n_resets
        self._ctrl = ctrl
        self._label = label

        if ctrl is not None:
            self._ctrl_size = ctrl.n_qubits
            register_name = "{} control".format(label)
            self._register = QuantumRegister(self._ctrl_size,register_name) if label else QuantumRegister(self._ctrl_size) 
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




    




class OneWayBoundaryControl(BoundaryControl):

    def __init__(self,bitstring, dimension = 0, ctrl_state=None,n_control_qubits = 4, n_resets=2, label=None) -> None:
        ctrl = CylicController(n_qubits=n_control_qubits)
        super().__init__(ctrl, ctrl_state, n_resets, label)
        boundary = Boundary(bitstring,dimension, label)
        self.add_boundary(boundary)