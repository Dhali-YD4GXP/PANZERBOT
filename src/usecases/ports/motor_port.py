from abc import ABC, abstractmethod
from src.domain.models import MotorSpeed

class MotorPort(ABC):
    """Interface (port) untuk mengendalikan hardware motor driver L298N."""

    @abstractmethod
    def set_speed(self, speed: MotorSpeed) -> None:
        """Mengatur kecepatan motor kiri dan kanan secara independen."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Menghentikan kedua motor secara total."""
        pass
