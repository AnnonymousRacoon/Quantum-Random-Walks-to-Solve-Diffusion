
from qiskit import QuantumCircuit
from qiskit.circuit import ControlledGate, Gate
from DiffusionProject.Algorithms.BuildingBlocks import qft
from qiskit.quantum_info.operators import Operator
import numpy as np
from numpy import pi, cos, sin, exp


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


class DFTCoin(Coin):
    def __init__(self, n_qubits) -> None:
        super().__init__(n_qubits)
        self._name = "DFT Coin"
        qft(self._control_circuit,n_qubits=n_qubits)
        self._gate = self._control_circuit.to_gate(label = self._name)



class PhaseKickbackCoin(Coin):
    def __init__(self, n_qubits,lam) -> None:
        super().__init__(n_qubits)
        self._name = "Phase Kickback Coin"

        qubit_indices = [i for i in range(n_qubits)]

        #  -----------Diffuser Protocol
        # Apply transformation |s> -> |00..0> (H-gates)
        self._control_circuit.h(qubit_indices)
        # Apply transformation |00..0> -> |11..1> (X-gates)
        self._control_circuit.x(qubit_indices)
        # Do multi-controlled-Z gate
        self._control_circuit.mcp(lam,qubit_indices[:-1], [-1])  # multi-controlled-toffoli
        # Apply transformation |11..1> -> |00..0>
        self._control_circuit.x(qubit_indices)
        # Apply transformation |00..0> -> |s>
        self._control_circuit.h(qubit_indices)
         #  -----------
        
        self._gate = self._control_circuit.to_gate(label = self._name)


class RightKickBackCoin(PhaseKickbackCoin):
    """
        A Quantum coin similiar to a Grover coin which performs kickback with phase pi/2
        """
    def __init__(self, n_qubits) -> None:
        """
        A Quantum coin similiar to a Grover coin which performs kickback with phase pi/2
        """
        super().__init__(n_qubits, pi/2.0)
        self._name = "Right Kickback Coin"

class RightPlusKickBackCoin(PhaseKickbackCoin):
    """
        A Quantum coin similiar to a Grover coin which performs kickback with phase pi/4
        """
    def __init__(self, n_qubits) -> None:
        """
        A Quantum coin similiar to a Grover coin which performs kickback with phase pi/4
        """
        super().__init__(n_qubits, pi/4.0)
        self._name = "Right Plus Kickback Coin"

class RightMinusKickBackCoin(PhaseKickbackCoin):
    """
        A Quantum coin similiar to a Grover coin which performs kickback with phase 3pi/4
        """
    def __init__(self, n_qubits) -> None:
        """
        A Quantum coin similiar to a Grover coin which performs kickback with phase 3pi/4
        """
        super().__init__(n_qubits, 3*pi/4.0)
        self._name = "Right Minus Kickback Coin"


class LeftKickBackCoin(PhaseKickbackCoin):
    """
        A Quantum coin similiar to a Grover coin which performs kickback with phase 3pi/2
        """
    def __init__(self, n_qubits) -> None:
        """
        A Quantum coin similiar to a Grover coin which performs kickback with phase 3pi/2
        """
        super().__init__(n_qubits, 3*pi/2.0)
        self._name = "Left Kickback Coin"

class LeftMinusKickBackCoin(PhaseKickbackCoin):
    """
        A Quantum coin similiar to a Grover coin which performs kickback with phase 5pi/4
        """
    def __init__(self, n_qubits) -> None:
        """
        A Quantum coin similiar to a Grover coin which performs kickback with phase 5pi/4
        """
        super().__init__(n_qubits, 5*pi/4.0)
        self._name = "Left Minus Kickback Coin"

class LeftPlusKickBackCoin(PhaseKickbackCoin):
    """
        A Quantum coin similiar to a Grover coin which performs kickback with phase 7pi/4
        """
    def __init__(self, n_qubits) -> None:
        """
        A Quantum coin similiar to a Grover coin which performs kickback with phase 7pi/4
        """
        super().__init__(n_qubits, 7*pi/4.0)
        self._name = "Left Plus Kickback Coin"

        
class SU2BasicCoin(Coin):
    def __init__(self, n_qubits,theta,zeta,xi) -> None:
        super().__init__(n_qubits)
        self._name = "SU2 Coin"
        SU2_arr = np.array([[exp(1j*xi)*cos(theta), exp(1j*zeta)*sin(theta)],
                [exp(-1j*zeta)*sin(theta), -exp(-1j*xi)*cos(theta)]])
        SU2 = Operator(SU2_arr)
        for qubit_idx in range(n_qubits):
            self._control_circuit.append(SU2, [qubit_idx])
    
        self._gate = self._control_circuit.to_gate(label = self._name)


    
class SU2Coin(Coin):
    def __init__(self, n_qubits,theta,zeta,xi) -> None:
        super().__init__(n_qubits)
        self._name = "SU2 Coin"

        if type(theta) == list:
            assert len(theta) == n_qubits, "Value error, len(theta) must be equal to the number of qubits"
        else:
            theta = [theta for _ in range(n_qubits)]
        
        if type(zeta) == list:
            assert len(zeta) == n_qubits, "Value error, len(zeta) must be equal to the number of qubits"
        else:
            zeta = [zeta for _ in range(n_qubits)]

        if type(xi) == list:
            assert len(xi) == n_qubits, "Value error, len(xi) must be equal to the number of qubits"
        else:
            xi = [xi for _ in range(n_qubits)]
        
        for qubit_idx in range(n_qubits):

            SU2_arr = np.array([[exp(1j*xi[qubit_idx])*cos(theta[qubit_idx]), exp(1j*zeta[qubit_idx])*sin(theta[qubit_idx])],
                    [exp(-1j*zeta[qubit_idx])*sin(theta[qubit_idx]), -exp(-1j*xi[qubit_idx])*cos(theta[qubit_idx])]])
            SU2 = Operator(SU2_arr)
        
            self._control_circuit.append(SU2, [qubit_idx])

    
        self._gate = self._control_circuit.to_gate(label = self._name)
