from DiffusionProject.Algorithms.Coins import HadamardCoin, GroverCoin, CylicController, DFTCoin, PhaseKickbackCoin, RightKickBackCoin, LeftKickBackCoin, RightMinusKickBackCoin, RightPlusKickBackCoin, LeftMinusKickBackCoin, LeftPlusKickBackCoin, SU2Coin
from DiffusionProject.Algorithms.Walks import QuantumWalk1D, QuantumWalk2D, QuantumWalk2DIndependant, QuantumWalk3D
from qiskit.test.mock import FakeToronto

walk_type_dict = {
    1: QuantumWalk1D,
    2: QuantumWalk2D,
    3: QuantumWalk3D,
    -1:QuantumWalk1D,
    -2:QuantumWalk2DIndependant,
    -3:QuantumWalk3D
}

coin_class_dict = {
    "N": None,
    "Hadamard": HadamardCoin,
    "H": HadamardCoin,
    "SU2": SU2Coin,
    "Grover": GroverCoin,
    "G": GroverCoin,
    "DFT": DFTCoin,
    "PhaseKickback":PhaseKickbackCoin,
    "PK":PhaseKickbackCoin,
    "RK": RightKickBackCoin,
    "RightKickback": RightKickBackCoin,
    "LK": LeftKickBackCoin,
    "LeftKickback": LeftKickBackCoin,
    "RPK": RightPlusKickBackCoin,
    "RMK": RightMinusKickBackCoin,
    "LPK": LeftPlusKickBackCoin,
    "LMK": LeftMinusKickBackCoin,
    "Cyclic_controller": CylicController
}

backend_dict = {
    "FakeToronto": FakeToronto

}