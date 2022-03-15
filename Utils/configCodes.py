from DiffusionProject.Algorithms.Coins import HadamardCoin, GroverCoin, CylicController, PhaseKickbackCoin, RightKickBackCoin, LeftKickBackCoin, RightMinusKickBackCoin, RightPlusKickBackCoin, LeftMinusKickBackCoin, LeftPlusKickBackCoin
from DiffusionProject.Algorithms.Walks import QuantumWalk1D, QuantumWalk2D, QuantumWalk3D

walk_type_dict = {
    1: QuantumWalk1D,
    2: QuantumWalk2D,
    3: QuantumWalk3D
}

coin_class_dict = {
    "N": None,
    "Hadamard": HadamardCoin,
    "H": HadamardCoin,
    "Grover": GroverCoin,
    "G": GroverCoin,
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