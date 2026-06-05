"""Abstract base for raw mouse listeners."""

import threading
import abc


class BaseMouseListener(abc.ABC):
    def __init__(self):
        self._delta_x = 0
        self._delta_y = 0
        self._lock = threading.Lock()
        self._start_lock = threading.Lock()
        self._thread = None
        self.running = False

    @abc.abstractmethod
    def _run(self):
        """Platform-specific event loop logic."""
        pass

    @abc.abstractmethod
    def stop(self):
        """Platform-specific teardown logic."""
        pass

    def start(self):
        """Universal start logic."""
        with self._start_lock:
            if self._thread and self._thread.is_alive():
                return
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def is_alive(self) -> bool:
        """Returns whether the listener thread is alive."""
        return self._thread is not None and self._thread.is_alive()

    def get_deltas(self) -> tuple[float, float]:
        """Retrieves mouse deltas."""
        with self._lock:
            return (self._delta_x, self._delta_y)

    def reset_deltas(self) -> None:
        """Resets mouse deltas to zero."""
        with self._lock:
            self._delta_x, self._delta_y = 0, 0

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
