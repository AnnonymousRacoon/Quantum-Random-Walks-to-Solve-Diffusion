from DiffusionProject.Algorithms.Coins import HadamardCoin, GroverCoin, CylicController
from DiffusionProject.Algorithms.Walks import Backend, QuantumWalk1D, QuantumWalk2D, QuantumWalk3D
from DiffusionProject.Algorithms.Boundaries import Boundary, OneWayBoundaryControl, BoundaryControl
from DiffusionProject.Evaluation.Experiments import Experiment, SingleExperiment
import argparse




my_parser = argparse.ArgumentParser(description='Run a Quantum Walk Simulation')
my_parser.add_argument('--ndims', action='store', type=int, required=True)
my_parser.add_argument('--nqubits', action='store', type=int, required=True)
my_parser.add_argument('--boundary', action='append')
my_parser.add_argument('--initital_states', action='store', type=str)
my_parser.add_argument('--coin', action='store', type=str)
my_parser.add_argument('--nsteps', action='store', type=int, default = 10)
my_parser.add_argument('--shots', action='store', type=int, default = 2048)
my_parser.add_argument('--GPU', action='store_true', default = False)
args = vars(my_parser.parse_args())
print(args)


BACKEND = Backend(use_GPU=args.get("GPU"))


coin_class_dict = {
    "N": None,
    "Hadamard": HadamardCoin,
    "H": HadamardCoin,
    "Grover": GroverCoin,
    "G": GroverCoin,
    "Cyclic_controller": CylicController
}

walk_type_dict = {
    1: QuantumWalk1D,
    2: QuantumWalk2D,
    3: QuantumWalk3D
}


def generate_boundary_control_code_dict():
    boundaries = {}

    if args.get("boundary"):
        # Boundary format: type-dimension-bitstring-control_class-n_boundary_qubits
        #                  e.g hard-0-1111-Hadamard-1
        for boundary in args.get("boundary"):
            boundary_args = boundary.split("-")
            boundary_type, boundary_dimension, boundary_bitstring = boundary_args[0], int(boundary_args[1]), boundary_args[2]
            new_boundary = Boundary(boundary_bitstring,dimension=boundary_dimension)


            if boundary_type.lower() == 'h' or boundary_type.lower() == 'hard':
                control_code = "N-0"
                
            elif boundary_type.lower() == 's' or boundary_type.lower() == 'soft':
                
                if len(boundary_args) == 5 and boundary_args[4] != "":
                    n_boundary_qubits = boundary_args[4]
                else:
                    n_boundary_qubits = 1

                control_name = boundary_args[3]
                control_code = f"{control_name}-{n_boundary_qubits}"

            if boundaries.get(control_code):
                    boundaries[control_code].append(new_boundary)
            else:
                    boundaries[control_code] = [new_boundary]
            

    return boundaries


def generate_boundary_controls():
    control_code_dict = generate_boundary_control_code_dict()
    boundary_controls = []
    for code, boundaries in control_code_dict.items():
        

        boundary_control_class = coin_class_dict.get(code.split("-")[0],HadamardCoin)
        print(code)
        n_boundary_qubits = int(code.split("-")[1])
        if boundary_control_class:
            boundary_control_coin = boundary_control_class(n_boundary_qubits)
        else:
            boundary_control_coin = None

        new_boundary_control = BoundaryControl(ctrl = boundary_control_coin)
        new_boundary_control.add_boundaries(boundaries)
        boundary_controls.append(new_boundary_control)

    return boundary_controls




kwargs = {}
kwargs["system_dimensions"] = [args.get("nqubits")]*args.get("ndims") if args.get("ndims") > 1 else args.get("nqubits")

if args.get("initial_states","auto") == "auto":
    middle_bitstring = "0"+"1"*(args.get("nqubits")-1)
    kwargs["initial_states"] = [middle_bitstring]*args.get("ndims")
    
else:
    kwargs["initial_states"] = args.get("initial_states").split()

kwargs["boundary_controls"] = generate_boundary_controls()
kwargs["coin_class"] = coin_class_dict.get(args.get("coin"), HadamardCoin)
kwargs["backend"] = BACKEND

walk_class = walk_type_dict.get(args["ndims"])
walk = walk_class(**kwargs)
Experiment = SingleExperiment(walk,args["ndims"],args["nqubits"],args["shots"],args["nsteps"])
Experiment.run()


