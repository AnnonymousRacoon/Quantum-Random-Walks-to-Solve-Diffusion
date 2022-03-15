import argparse

class ExperimentParser:
    def __init__(self) -> None:
        self.__parser = argparse.ArgumentParser(description='Run a Quantum Walk Simulation')
        self.__parser.add_argument('--ndims', action='store', type=int, required=True)
        self.__parser.add_argument('--nqubits', action='store', type=int, required=True)
        self.__parser.add_argument('--boundary', action='append')
        self.__parser.add_argument('--initital_states', action='store', type=str)
        self.__parser.add_argument('--coin', action='store', type=str)
        self.__parser.add_argument('--coin', action='store', type=str)
        self.__parser.add_argument('--coin_kwargs', action='store', type=str)
        self.__parser.add_argument('--nsteps', action='store', type=int, default = 10)
        self.__parser.add_argument('--shots', action='store', type=int, default = 2048)
        self.__parser.add_argument('--GPU', action='store_true', default = False)
        self.__parser.add_argument('--IBMDeviceName', action='store', type=str)
        self.__args = None

    def parse_args(self) -> dict:
        self.__args = vars(self.__parser.parse_args())
        return self.__args

    @property
    def args(self):
        if self.__args:
            return self.__args
        return self.parse_args()