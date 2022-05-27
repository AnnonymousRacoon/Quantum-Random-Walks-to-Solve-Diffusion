from abc import ABC, abstractmethod
from numpy import pi

class CoinInitialiser(ABC):

    
    def __init__(self) -> None:
        self._u1 = pi/2
        self._u2 = pi/2
        self._u3 = 3*pi/2

   
    def initialise(self,circuit,register):
        """Initialises the quantum coin"""
        circuit.u(self._u1,self._u2,self._u3,register[:])


class SymetricInitialiser(CoinInitialiser):
   
    
    def __init__(self) -> None:
        super().__init__()


    def initialise(self, circuit, register):
        """initialises the coin to traverse in symetric superposition"""
        if register.size == 2:
            circuit.u(pi/2,pi/2,3*pi/2,register[0])
            circuit.u(pi/2,3*pi/2,pi/2,register[1])
        
        else:
            return super().initialise(circuit, register)
        

        

class AsymetricInitialiser(CoinInitialiser):

    def __init__(self) -> None:
        self._u1 = 0
        self._u2 = 0
        self._u3 = 0


class CustomUnitaryInitialiser(CoinInitialiser):
    def __init__(self,U_array: list) -> None:
        for U in U_array:
            assert len(U) == 3
        self._U_array = U_array

    def initialise(self,circuit,register):
        """Initialises the quantum coin"""
        for idx in range(register.size):
            U = self._U_array[idx]
            circuit.u(*U,register[idx])
        return

    
