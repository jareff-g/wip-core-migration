"""
****************************************************************************************************************
Class ProcessingWorker
Handles AfterScan processing (stabilization, cropping, other miscellaneous graphics processing)

Licensed under a MIT LICENSE.

More info in README.md file
****************************************************************************************************************
"""
__author__ = 'Juan Remirez de Esparza'
__copyright__ = "Copyright 2022/24, Juan Remirez de Esparza"
__credits__ = ["Juan Remirez de Esparza"]
__license__ = "MIT"
__module__ = "processing_worker"
__version__ = "1.0.0"
__date__ = "2025-12-15"
__version_highlight__ = "ProcessingWorker - First version (stub for now)"
__maintainer__ = "Juan Remirez de Esparza"
__email__ = "jremirez@hotmail.com"
__status__ = "Development"


import threading
from queue import Queue

class ProcessingWorker(threading.Thread):
    """
    A worker thread responsible for consuming tasks and producing results.
    It receives the queues as dependencies from the MainApp.
    """
    def __init__(self, input_queue: Queue, output_queue: Queue):
        super().__init__()
        # Store the required communication endpoints
        self.input_queue = input_queue
        self.output_queue = output_queue
        self._stop_event = threading.Event()

    def run(self):
        """
        The main processing loop.
        In the final implementation, this loop will continually check
        the input_queue for new tasks.
        """
        print(f"{self.name}: Starting up...")
        while not self._stop_event.is_set():
            # Placeholder for future logic:
            # try:
            #     task = self.input_queue.get(timeout=1)
            #     result = self._process_task(task)
            #     self.output_queue.put(result)
            #     self.input_queue.task_done()
            # except queue.Empty:
            #     continue
            self._stop_event.wait(0.5) # Wait briefly to prevent high CPU usage
        print(f"{self.name}: Shutting down.")

    def stop(self):
        """Signals the thread to stop execution."""
        self._stop_event.set()

    def _process_task(self, task):
        """Internal method placeholder for processing logic."""
        # Future: Complex CPU-bound work goes here
        return f"Processed: {task}"

    def submit_task(self, task):
        """A simple proxy method to put a task onto the input queue."""
        self.input_queue.put(task)