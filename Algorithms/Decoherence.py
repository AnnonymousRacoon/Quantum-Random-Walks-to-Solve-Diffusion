

class CoinDecoherenceCycle:
    def __init__(self,cycle_length: int,target_qubits: list) -> None:
        self._cycle_length = cycle_length
        self._target_qubits = target_qubits    

    @property
    def cycle_length(self)->int:
        return self._cycle_length

    @cycle_length.setter
    def cycle_length(self,length)-> None:
        self._cycle_length = length

    @property
    def target_qubits(self)->list:
        return self._target_qubits

    @target_qubits.setter
    def target_qubits(self, nqubits)->None:
        self._target_qubits = nqubits



    

    