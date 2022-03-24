from math import pi

def qft_rotations(circuit, n_qubits):
    """Performs qft on the first n qubits in circuit (without swaps)"""
    if n_qubits == 0:
        return circuit
    n = n_qubits-1
    circuit.h(n)
    for qubit in range(n):
        circuit.cp(pi/2**(n-qubit), qubit, n)
    # At the end of our function, we call the same function again on
    # the next qubits (we reduced n by one earlier in the function)
    qft_rotations(circuit, n)

    return circuit

def swap_registers(circuit, n_qubits):
    for qubit_idx in range(n_qubits//2):
        circuit.swap(qubit_idx, n_qubits-qubit_idx-1)
    return circuit

def qft(circuit, n_qubits):
    """QFT on the first n qubits in circuit"""
    qft_rotations(circuit, n_qubits)
    swap_registers(circuit, n_qubits)
    return circuit


def grover_diffuser(circuit, n_qubits):
    """Applies the grover diffuser on the first n qubits in circuit"""
    qubit_indices = [i for i in range(n_qubits)]

    #  -----------Diffuser Protocol
    # Apply transformation |s> -> |00..0> (H-gates)
    circuit.h(qubit_indices)
        # Apply transformation |00..0> -> |11..1> (X-gates)
    circuit.x(qubit_indices)
        # Do multi-controlled-Z gate
    circuit.h([-1])
    circuit.mct(qubit_indices[:-1], [-1])  # multi-controlled-toffoli
    circuit.h([-1])
        # Apply transformation |11..1> -> |00..0>
    circuit.x(qubit_indices)
        # Apply transformation |00..0> -> |s>
    circuit.h(qubit_indices)
    
    return circuit