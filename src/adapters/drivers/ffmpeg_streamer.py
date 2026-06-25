import subprocess
import time
import threading
import os
from src.usecases.ports.video_streamer_port import VideoStreamerPort

class FFmpegStreamer(VideoStreamerPort):
    """Implementasi VideoStreamerPort menggunakan FFmpeg.
    Mengirimkan stream MJPEG secara langsung ke port HTTP.
    Menggunakan mode '-listen 1' yang akan disajikan secara loop pada thread terpisah.
    """

    def __init__(self, device: str = "/dev/video0", port: int = 8888, resolution: str = "640x480", framerate: int = 30):
        self.device = device
        self.port = port
        self.resolution = resolution
        self.framerate = str(framerate)
        self.process = None
        self.is_running = False
        self.thread = None

    def start_streaming(self) -> None:
        """Memulai stream video pada thread latar belakang."""
        if self.is_running:
            print("[FFmpegStreamer] Streamer sudah berjalan.")
            return

        self.is_running = True
        
        # Bersihkan terlebih dahulu proses mediamtx dan ffmpeg lama agar device kamera bebas
        self._cleanup_conflicting_processes()

        self.thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.thread.start()
        print(f"[FFmpegStreamer] Server MJPEG langsung berjalan di http://0.0.0.0:{self.port} (kamera: {self.device})")

    def _cleanup_conflicting_processes(self) -> None:
        """Menghentikan proses mediamtx dan ffmpeg yang sedang berjalan untuk membebaskan /dev/video0."""
        print("[FFmpegStreamer] Membersihkan proses ffmpeg/mediamtx lama...")
        try:
            subprocess.run(["pkill", "-f", "mediamtx"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-f", "ffmpeg"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1) # Beri jeda sistem untuk menutup file descriptor kamera
        except Exception as e:
            print(f"[FFmpegStreamer] Peringatan saat pkill: {e}")

    def _stream_loop(self) -> None:
        """Loop utama untuk menjalankan ffmpeg. Mengulang ketika klien terputus."""
        while self.is_running:
            # Command FFmpeg:
            # -f v4l2: input format video4linux2
            # -input_format mjpeg: menggunakan decoder hardware mjpeg bawaan webcam logitech agar hemat CPU
            # -video_size: resolusi video
            # -framerate: fps video
            # -i: input device
            # -c:v copy: copy stream video tanpa encoding ulang (hemat CPU!)
            # -f mpjpeg: output format multipart jpeg (mjpeg stream)
            # -listen 1: bertindak sebagai server HTTP yang melayani 1 koneksi lalu keluar
            cmd = [
                "ffmpeg",
                "-y",
                "-f", "v4l2",
                "-input_format", "mjpeg",
                "-video_size", self.resolution,
                "-framerate", self.framerate,
                "-i", self.device,
                "-c:v", "copy",
                "-f", "mpjpeg",
                "-listen", "1",
                f"http://0.0.0.0:{self.port}"
            ]
            
            try:
                # Buka devnull agar log ffmpeg yang sangat berisik tidak membanjiri terminal
                devnull = open(os.devnull, 'wb')
                self.process = subprocess.Popen(
                    cmd,
                    stdout=devnull,
                    stderr=devnull
                )
                # Tunggu hingga klien disconnect dan ffmpeg selesai
                self.process.wait()
            except Exception as e:
                if self.is_running:
                    print(f"[FFmpegStreamer] Error saat menjalankan ffmpeg: {e}")
                time.sleep(2)
            finally:
                # Pastikan proses ditutup jika error
                if self.process:
                    try:
                        self.process.kill()
                    except:
                        pass
                    self.process = None

            # Jeda kecil sebelum restart agar tidak spamming jika ada error persisten (misal kamera dicabut)
            time.sleep(0.5)

    def stop_streaming(self) -> None:
        """Menghentikan stream video."""
        self.is_running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try:
                    self.process.kill()
                except:
                    pass
            except Exception:
                pass
            self.process = None
        print("[FFmpegStreamer] Stream video dihentikan.")
