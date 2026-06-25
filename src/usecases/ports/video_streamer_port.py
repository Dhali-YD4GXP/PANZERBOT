from abc import ABC, abstractmethod

class VideoStreamerPort(ABC):
    """Interface (port) untuk memulai dan menghentikan streaming video langsung."""

    @abstractmethod
    def start_streaming(self) -> None:
        """Memulai stream video."""
        pass

    @abstractmethod
    def stop_streaming(self) -> None:
        """Menghentikan stream video."""
        pass
