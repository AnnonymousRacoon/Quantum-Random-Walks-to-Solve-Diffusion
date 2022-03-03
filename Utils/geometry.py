from DiffusionProject.Utils.binaryMethods import binary_step_up, binary_step_down

class BoundaryGenerator:
    
    @staticmethod
    def generate_boundaries(geometry_class, n_qubits, padding = 0):
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

            

        for bin_value,shift in zip(bin_vals,shifts):
            edge = bin_value*n_qubits
            for _ in range(padding):
                edge = shift(edge)
            bitstrings.append(edge)

        
        return bitstrings

