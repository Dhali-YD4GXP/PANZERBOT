from abc import ABC, abstractmethod
from src.domain.models import CameraOrientation

class ServoPort(ABC):
    """Interface (port) untuk mengendalikan hardware servo pan-tilt camera."""

    @abstractmethod
    def set_orientation(self, orientation: CameraOrientation) -> None:
        """Mengatur sudut servo pan dan tilt."""
        pass

    @abstractmethod
    def get_orientation(self) -> CameraOrientation:
        """Mendapatkan orientasi sudut pan dan tilt kamera saat ini."""
        pass
