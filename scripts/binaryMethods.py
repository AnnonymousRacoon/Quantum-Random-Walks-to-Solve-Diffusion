

def flip_bit(bit: str) -> str:
    """returns the input bit flipped"""
    assert bit == "0" or bit =="1"
    return "0" if bit =="1" else "1"

def binary_step_up(bitstring: str) -> str:
    """returns the input bitstring cyclically incremented by 1"""
    bitstring = [char for char in bitstring]
    n_bits = len(bitstring)

    bit_idx = 0

    while bit_idx < n_bits-1:
        if "".join(bitstring[bit_idx+1:]) == "1" * len(bitstring[bit_idx+1:]):
            bitstring[bit_idx] = flip_bit(bitstring[bit_idx])
        bit_idx+=1

    bitstring[-1] = flip_bit(bitstring[-1])

    return "".join(bitstring)

def binary_step_down(bitstring: str) -> str:
    """returns the input bitstring cyclically decremented by 1"""

    bitstring = [char for char in bitstring]
    n_bits = len(bitstring)

    bitstring[-1] = flip_bit(bitstring[-1])

    bit_idx = n_bits-2

    while bit_idx >=0:
        if "".join(bitstring[bit_idx+1:]) == "1" * len(bitstring[bit_idx+1:]):
            bitstring[bit_idx] = flip_bit(bitstring[bit_idx])
        bit_idx-=1

    return "".join(bitstring)