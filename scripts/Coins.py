
from qiskit import QuantumCircuit
from qiskit.circuit import ControlledGate, Gate


class Control:

    def __init__(self,n_qubits) -> None:
        self._name = "Identity"
        self._n_qubits = n_qubits
        self._control_circuit = QuantumCircuit(n_qubits)
        self._gate = self._control_circuit.to_gate(label = self._name)
        
    
    @property
    def gate(self) -> Gate:
        return self._gate

    @property
    def n_qubits(self) -> int:
        return self._n_qubits

    def control(self, num_ctrl_qubits,ctrl_state = None, inverse = False, label = None) -> ControlledGate:
        if ctrl_state == None:
            ctrl_state = "1"*num_ctrl_qubits

        base_gate = self._gate if not inverse else self.inverse()
        if inverse:
            base_gate.name = "${}$".format(self._name + r"^{-1}")
        return base_gate.control(num_ctrl_qubits,ctrl_state = ctrl_state, label = label)


    def inverse(self):
        return self._gate.inverse()



class CylicController(Control):
    def __init__(self, n_qubits) -> None:
        super().__init__(n_qubits)
        self._name = "Cyclic Controller"
        self._control_circuit.x(0)
        for idx in range(1,n_qubits):
            control_indices = [i for i in range(idx)]
            self._control_circuit.mct(control_indices,idx)
        self._gate = self._control_circuit.to_gate(label = self._name)

    


class Coin(Control):
    def __init__(self, n_qubits) -> None:
        super().__init__(n_qubits)
    
    @property
    def DReversalGate(self):
        qc = QuantumCircuit(self._n_qubits)
        qc.x(-1)
        directional_reversal_gate = qc.to_gate(label = "Direction Reversal")
        return directional_reversal_gate
    
class XCoin(Coin):
    def __init__(self, n_qubits) -> None:
        super().__init__(n_qubits)
        self._name = "X Coin"
        qubit_indices = [i for i in range(n_qubits)]
        self._control_circuit.x(qubit_indices)
        self._gate = self._control_circuit.to_gate(label = self._name)


class HadamardCoin(Coin):

    def __init__(self,n_qubits) -> None:
        super().__init__(n_qubits)
        self._name = "Hadamard Coin"
        qubit_indices = [i for i in range(n_qubits)]
        self._control_circuit.h(qubit_indices)
        self._gate = self._control_circuit.to_gate(label = self._name)


class GroverCoin(Coin):
    def __init__(self, n_qubits) -> None:
        super().__init__(n_qubits)
        self._name = "Grover Coin"

        qubit_indices = [i for i in range(n_qubits)]

        #  -----------Diffuser Protocol
        # Apply transformation |s> -> |00..0> (H-gates)
        self._control_circuit.h(qubit_indices)
        # Apply transformation |00..0> -> |11..1> (X-gates)
        self._control_circuit.x(qubit_indices)
        # Do multi-controlled-Z gate
        self._control_circuit.h([-1])
        self._control_circuit.mct(qubit_indices[:-1], [-1])  # multi-controlled-toffoli
        self._control_circuit.h([-1])
        # Apply transformation |11..1> -> |00..0>
        self._control_circuit.x(qubit_indices)
        # Apply transformation |00..0> -> |s>
        self._control_circuit.h(qubit_indices)
         #  -----------
        
        self._gate = self._control_circuit.to_gate(label = self._name)
        

        



    
