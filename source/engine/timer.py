import time


class Timer:

    def __init__(self):
        self.end_ticks = None

    def start(self, duration: float):
        """ Starts the timer

        arguments
        - time: number of seconds until the timer should finish
        """

        self.end_ticks = time.time() + duration

    def finished(self) -> bool:
        """ Checks whether the timer is finished """
        return time.time() >= self.end_ticks
    
    def delta(self) -> int:
        """ Gets the number of milliseconds (signed) between the current time
        and the timer's end """

        return self.end_ticks - time.time()