import os
import subprocess
from src.usecases.ports.speaker_port import SpeakerPort

class SpeakerDriver(SpeakerPort):
    """Implementasi SpeakerPort untuk memutar file suara pada Raspberry Pi.
    Menggunakan subproses eksternal (seperti aplay atau mpg123) untuk memutar berkas audio.
    """

    def __init__(self, sounds_dir: str = None):
        if sounds_dir is None:
            # Ambil path relatif dari root proyek untuk folder 'sounds'
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            # current_file_dir adalah src/adapters/drivers
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir)))
            sounds_dir = os.path.join(project_root, "sounds")

        self.sounds_dir = sounds_dir
        self.active_processes = []

        # Buat direktori soundboard jika belum ada
        if not os.path.exists(sounds_dir):
            try:
                os.makedirs(sounds_dir)
                print(f"[SpeakerDriver] Membuat direktori soundboard di: {sounds_dir}")
            except Exception as e:
                print(f"[SpeakerDriver] Gagal membuat direktori soundboard: {e}")

    def play_sound(self, sound_name: str) -> None:
        """Memutar file audio yang tersimpan di direktori sounds_dir."""
        # Bersihkan proses pemutaran audio yang sudah selesai dari list
        self.active_processes = [p for p in self.active_processes if p.poll() is None]

        # Cari file audio (mendukung .wav dan .mp3)
        file_path = None
        player_cmd = None

        for ext in [".wav", ".mp3"]:
            path = os.path.join(self.sounds_dir, f"{sound_name}{ext}")
            if os.path.exists(path):
                file_path = path
                player_cmd = "aplay" if ext == ".wav" else "mpg123"
                break

        if not file_path:
            print(f"[SpeakerDriver] File suara '{sound_name}' tidak ditemukan di {self.sounds_dir}")
            # Mode Simulasi jika file tidak ada
            print(f"[SpeakerDriver SIMULASI] Memutar suara: {sound_name}")
            return

        try:
            # Jalankan command player secara asinkron agar tidak memblokir thread kontrol utama
            # Output dialihkan ke /dev/null agar tidak mengotori console log utama
            devnull = open(os.devnull, 'wb')
            process = subprocess.Popen(
                [player_cmd, file_path],
                stdout=devnull,
                stderr=devnull
            )
            self.active_processes.append(process)
            print(f"[SpeakerDriver] Memutar file audio: {file_path}")
        except Exception as e:
            print(f"[SpeakerDriver] Gagal memutar file audio '{file_path}': {e}")

    def stop_all(self) -> None:
        """Menghentikan semua pemutaran suara."""
        count = 0
        for process in self.active_processes:
            if process.poll() is None:  # Jika masih berjalan
                try:
                    process.terminate()
                    count += 1
                except Exception as e:
                    print(f"[SpeakerDriver] Gagal menghentikan proses audio: {e}")
        
        self.active_processes.clear()
        if count > 0:
            print(f"[SpeakerDriver] Menghentikan {count} proses pemutaran audio.")
