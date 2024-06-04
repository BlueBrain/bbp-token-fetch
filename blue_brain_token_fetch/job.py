import threading
import signal
from datetime import timedelta
from typing import Callable, List


class InterruptionStack:
    stack: List[Callable] = []

    @classmethod
    def callable_stack(cls):
        for c in InterruptionStack.stack:
            c()


class Job(threading.Thread):
    def __init__(self, interval, execute):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute

    def stop(self):
        self.stopped.set()
        # self.join()

    def run(self):
        while not self.stopped.wait(self.interval.total_seconds()):
            self.execute()

    @staticmethod
    def schedule(execute, interval, interruption_str="") -> Callable:
        """Returns handle to be capable of manually interrupt the job"""

        job = Job(interval=timedelta(seconds=interval), execute=execute)

        def test():
            print(f"Program killed: {interruption_str}")
            job.stop()

        InterruptionStack.stack.append(test)
        signal.signal(signal.SIGTERM, lambda a, b: InterruptionStack.callable_stack())
        signal.signal(signal.SIGINT, lambda a, b: InterruptionStack.callable_stack())

        job.start()

        return lambda: job.stop()
