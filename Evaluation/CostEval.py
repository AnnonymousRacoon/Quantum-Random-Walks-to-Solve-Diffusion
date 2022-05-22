from qiskit import QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import Unroller

default_cost_dict = {
                    'u': 1,
                    'u3':1,
                    'cx':10,
                    'qubits':100
                    }

def unroll_circuit(circuit: QuantumCircuit, unroller_args = None):
    """unrolls a quantum circuit"""
 
    if not unroller_args:
        unroller_args = ['u3', 'cx','u']

    pass_ = Unroller(unroller_args)
    pass_manager = PassManager(pass_)
    unrolled_circuit = pass_manager.run(circuit) 
    return unrolled_circuit

def calculate_circuit_cost(circuit: QuantumCircuit, cost_dict = None, unroller_args = None):
    """Calculates the cost of a quantum circuit"""

    if not cost_dict:
        cost_dict = default_cost_dict

    unrolled_circuit = unroll_circuit(circuit, unroller_args)
    ops_counts = unrolled_circuit.count_ops()

    # compute cost
    cost = 0
    for op, n_op_applications in ops_counts.items():
        cost+= n_op_applications*cost_dict.get(op,0)

    cost += cost_dict.get('qubits',0)*unrolled_circuit.num_qubits

    return cost