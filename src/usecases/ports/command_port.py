from abc import ABC, abstractmethod
from typing import Callable
from src.domain.models import JoystickInput

class CommandPort(ABC):
    """Interface (port) untuk mendengarkan/menerima perintah dari aplikasi pengendali."""

    @abstractmethod
    def start_listening(
        self,
        on_tank_joystick: Callable[[JoystickInput], None],
        on_camera_joystick: Callable[[JoystickInput], None],
        on_soundboard: Callable[[str], None]
    ) -> None:
        """Mulai mendengarkan perintah dari luar (misal: websocket/WebRTC data channel)
        dan memicu callback yang sesuai.
        """
        pass

    @abstractmethod
    def stop_listening(self) -> None:
        """Menghentikan penerimaan perintah."""
        pass
