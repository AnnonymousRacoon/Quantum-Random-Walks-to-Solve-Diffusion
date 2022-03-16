
from qiskit import Aer
from qiskit.providers.aer import AerError, AerSimulator
from qiskit import IBMQ



class Backend:
    """wrapper for Qiskit backend """
    def __init__(self,use_GPU = False, IBMQ_device_name = None, backend = None) -> None:

        if IBMQ_device_name:
          
            IBMQ.load_account()
            self.__provider  = IBMQ.get_provider(hub='ibm-q')
            self.__backend = self.__provider.get_backend(IBMQ_device_name)
            self.__device = IBMQ_device_name
            self.__is_on_IBM = True
        
        else:
            if backend:
                self.__backend = AerSimulator.from_backend(backend)
            else:
                self.__backend = Aer.get_backend('aer_simulator')
            self.__device = "CPU" 
            self.__is_on_IBM = False
            # init GPU backend
            if use_GPU:
                try:
                    self.__backend.set_options(device='GPU')
                    self.__device = "GPU"
                except AerError as e:
                    print(e)

        print("running on device: {}".format(self.__device))
        print("Backend: {}".format(self.__backend.name()))

    @property
    def backend(self):
        return self.__backend

    @property
    def device(self):
        return self.__device

    @property
    def is_on_IBM(self):
        return self.__is_on_IBM