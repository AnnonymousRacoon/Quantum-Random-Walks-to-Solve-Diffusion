from qiskit import QuantumRegister
from DiffusionProject.Algorithms.Coins import Coin, CylicController

class Boundary:

    def __init__(self,bitstring: str, ctrl: Coin = None, ctrl_state = None, dimension = 0, label = None) -> None:
        self._bitstring = bitstring

        if ctrl is not None:
            self._ctrl_size = ctrl.n_qubits
            register_name = "{} control".format(label)
            self._register = QuantumRegister(self._ctrl_size,register_name) if label else QuantumRegister(self._ctrl_size) 
        else:
            self._ctrl_size = 0
            self._register = None

        self._ctrl = ctrl
        self._dimension = dimension
        self._label = label

        if ctrl is None:
            self._ctrl_state = ""

        elif ctrl is not None and ctrl_state is None:
            self._ctrl_state = "1"*ctrl.n_qubits


        elif ctrl_state != None:
            assert ctrl is not None
            assert len(ctrl_state) == ctrl.n_qubits
            self._ctrl_state = ctrl_state 


    @property
    def n_bits(self) -> int:
        """The length of the boundary bitstring"""
        return len(self._bitstring)

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def ctrl(self) -> Coin:
        return self._ctrl

    @property
    def register(self) -> QuantumRegister:
        return self._register

    @property
    def bitstring(self)-> str:
        return self._bitstring

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


class OneWayBoundary(Boundary):
    def __init__(self, bitstring: str, ctrl_state=None, n_boundary_cycle_bits = 3, dimension=0, label=None) -> None:
        ctrl = CylicController(n_boundary_cycle_bits)
        super().__init__(bitstring = bitstring, ctrl = ctrl, ctrl_state = ctrl_state, dimension = dimension, label = label)