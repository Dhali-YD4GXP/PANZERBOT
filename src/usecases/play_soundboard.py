from src.usecases.ports.speaker_port import SpeakerPort

class PlaySoundboardUseCase:
    """Use Case untuk memutar soundboard pada speaker tank."""

    def __init__(self, speaker_port: SpeakerPort):
        self._speaker_port = speaker_port

    def execute(self, sound_name: str) -> None:
        """Memulai pemutaran audio berdasarkan nama yang di-input dari aplikasi."""
        # Di sini kita bisa menambahkan validasi nama file suara jika diperlukan
        if not sound_name:
            return
        
        self._speaker_port.play_sound(sound_name)

    def stop(self) -> None:
        """Menghentikan semua pemutaran suara."""
        self._speaker_port.stop_all()
