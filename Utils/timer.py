import time
from datetime import timedelta
 
class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""
 
class Timer:
    """Times a process using the `time.process_time` module"""
    def __init__(self):
        self._start_time = None

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")
        self._start_time = time.process_time() 

    def stop(self):
        """Stop the timer, and return the elapsed time in seconds"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")
        elapsed_time = time.process_time()  - self._start_time
        self._start_time = None
        return float(f"{elapsed_time:0.4f}")

    @staticmethod
    def seconds_to_hms(seconds) -> str:
        """converts seconds to H:M:S format"""
        return str(timedelta(seconds=seconds))
