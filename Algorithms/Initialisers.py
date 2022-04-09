from abc import ABC, abstractmethod


class CoinInitialiser(ABC):

    @abstractmethod
    def initialise(self,circuit):
        pass


