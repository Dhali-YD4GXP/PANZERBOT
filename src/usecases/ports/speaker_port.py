from abc import ABC, abstractmethod

class SpeakerPort(ABC):
    """Interface (port) untuk memutar file suara pada speaker tank."""

    @abstractmethod
    def play_sound(self, sound_name: str) -> None:
        """Memutar file suara berdasarkan nama/identitas suara."""
        pass

    @abstractmethod
    def stop_all(self) -> None:
        """Menghentikan semua pemutaran suara yang sedang berjalan."""
        pass
