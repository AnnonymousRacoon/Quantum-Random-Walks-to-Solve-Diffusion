from DiffusionProject.Utils.binaryMethods import binary_step_up, binary_step_down
from DiffusionProject.Algorithms.Coins import HadamardCoin
from DiffusionProject.Algorithms.Boundaries import Boundary, OneWayBoundaryControl, BoundaryControl
from DiffusionProject.Utils.configCodes import coin_class_dict


class BoundaryGenerator:
    
    @staticmethod
    def generate_boundary_bitstrings(geometry_class, n_qubits, padding = 0):
        try:
            assert 2**(n_qubits-1) > padding
        except:
            raise ValueError("padding must not exceed centre of volume")

        bitstrings = []
        if geometry_class == "Edges":
            bin_vals = ["0", "1"]
            shifts = [binary_step_up,binary_step_down]

        elif geometry_class == "LeftEdge":
            bin_vals = ["0"]
            shifts = [binary_step_up]

        elif geometry_class == "RightEdge":
            bin_vals = ["1"]
            shifts = [binary_step_down]

        else:
            raise ValueError("geometry_class should be one of 'RightEdge', 'LeftEdge', 'Edges")

            
        # apply padding
        for bin_value,shift in zip(bin_vals,shifts):
            edge = bin_value*n_qubits
            for _ in range(padding):
                edge = shift(edge)
            bitstrings.append(edge)

        
        return bitstrings

    @staticmethod
    def generate_boundary_code(boundary_type,n_boundary_qubits,boundary_ctrl_type):
        """
        generates a boundary control code
        """
        if boundary_type.lower() == 'h' or boundary_type.lower() == 'hard':
            return "N-0"
                
        elif boundary_type.lower() == 's' or boundary_type.lower() == 'soft':

            return f"{boundary_ctrl_type}-{n_boundary_qubits}"
        
        raise ValueError("Unrecognised boundary type")


    @staticmethod
    def generate_boundary_controls(boundaries: list, boundary_control_codes: list) -> list:
        """
        generates a list of `BoundaryControl` objects from a list of `Boundary` objects and control codes
        """

        assert len(boundaries) == len(boundary_control_codes), "There must be the same number of control codes as boundaries"
        control_code_dict = {}
        for boundary, control_code in zip(boundaries,boundary_control_codes):
            if boundaries.get(control_code):
                    control_code_dict[control_code].append(boundary)
            else:
                    control_code_dict[control_code] = [boundary]
        
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


            

