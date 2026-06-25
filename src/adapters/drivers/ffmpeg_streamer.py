import subprocess
import time
import threading
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from src.usecases.ports.video_streamer_port import VideoStreamerPort

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Server HTTP yang mendukung multi-threading untuk melayani banyak klien secara paralel."""
    allow_reuse_address = True

class MJPEGHandler(BaseHTTPRequestHandler):
    """Request Handler untuk menyajikan stream MJPEG."""
    
    # Nonaktifkan logging HTTP bawaan agar tidak membanjiri terminal konsol
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.end_headers()
            
            try:
                # Loop mengirimkan frame JPEG terbaru ke klien secara terus-menerus
                while True:
                    streamer = self.server.streamer
                    if streamer and streamer.reader:
                        # Tunggu hingga frame baru tersedia
                        streamer.reader.frame_event.wait(timeout=1.0)
                        frame = streamer.reader.latest_frame
                        if frame:
                            self.wfile.write(b'--frame\r\n')
                            self.wfile.write(b'Content-Type: image/jpeg\r\n')
                            self.wfile.write(f'Content-Length: {len(frame)}\r\n\r\n'.encode())
                            self.wfile.write(frame)
                            self.wfile.write(b'\r\n')
                    else:
                        time.sleep(0.1)
            except (ConnectionResetError, BrokenPipeError):
                # Klien terputus secara normal
                pass
            except Exception as e:
                print(f"[MJPEGHandler] Error koneksi client: {e}")
        else:
            self.send_error(404)

class FrameReader(threading.Thread):
    """Thread khusus untuk membaca stream JPEG mentah dari stdout FFmpeg secara non-blocking."""
    
    def __init__(self, process):
        super().__init__(daemon=True)
        self.process = process
        self.latest_frame = None
        self.frame_event = threading.Event()
        self.is_running = True

    def run(self):
        stream = self.process.stdout
        buffer = bytearray()
        
        while self.is_running:
            # Baca data dalam chunk 4096 byte
            chunk = stream.read(4096)
            if not chunk:
                break
            buffer.extend(chunk)
            
            # Cari batas-batas gambar JPEG di dalam buffer
            while True:
                # SOI (Start of Image): 0xff 0xd8
                start = buffer.find(b'\xff\xd8')
                if start == -1:
                    # Buang data lama jika tidak ada penanda awal JPEG
                    if len(buffer) > 4096:
                        buffer = buffer[-4096:]
                    break
                
                # EOI (End of Image): 0xff 0xd9
                end = buffer.find(b'\xff\xd9', start)
                if end == -1:
                    # Data belum lengkap, keluar untuk membaca chunk berikutnya
                    break
                
                # Ekstrak data frame JPEG lengkap
                frame = buffer[start:end+2]
                self.latest_frame = frame
                
                # Beritahu semua client bahwa ada frame baru
                self.frame_event.set()
                self.frame_event.clear()
                
                # Hapus data frame yang sudah di-ekstrak dari buffer
                buffer = buffer[end+2:]

class FFmpegStreamer(VideoStreamerPort):
    """Implementasi VideoStreamerPort menggunakan FFmpeg dan Python HTTP Server.
    FFmpeg berjalan secara kontinu mengeluarkan JPEG ke stdout, lalu server Python
    mendistribusikannya ke banyak klien secara stabil tanpa memicu error restart kamera.
    """

    def __init__(self, device: str = "/dev/video0", port: int = 8888, resolution: str = "640x480", framerate: int = 30):
        self.device = device
        self.port = port
        self.resolution = resolution
        self.framerate = str(framerate)
        
        self.process = None
        self.reader = None
        self.http_server = None
        self.server_thread = None
        self.is_running = False

    def start_streaming(self) -> None:
        """Memulai streaming video dan server HTTP."""
        if self.is_running:
            print("[FFmpegStreamer] Streamer sudah berjalan.")
            return

        self.is_running = True
        
        # Bersihkan proses bertabrakan lama
        self._cleanup_conflicting_processes()

        # Jalankan FFmpeg untuk menulis stream JPEG mentah ke stdout
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "v4l2",
            "-input_format", "mjpeg",
            "-video_size", self.resolution,
            "-framerate", self.framerate,
            "-i", self.device,
            "-c:v", "copy",
            "-f", "mjpeg",
            "-"
        ]
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            print("[FFmpegStreamer] Subproses FFmpeg berhasil dimulai.")
        except Exception as e:
            print(f"[FFmpegStreamer] Gagal menjalankan FFmpeg: {e}")
            self.is_running = False
            return

        # Jalankan thread pembaca frame
        self.reader = FrameReader(self.process)
        self.reader.start()

        # Jalankan Python Threaded HTTP Server
        try:
            self.http_server = ThreadedHTTPServer(('0.0.0.0', self.port), MJPEGHandler)
            self.http_server.streamer = self
            self.server_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
            self.server_thread.start()
            print(f"[FFmpegStreamer] Server MJPEG stabil aktif di http://0.0.0.0:{self.port} (Kamera: {self.device})")
        except Exception as e:
            print(f"[FFmpegStreamer] Gagal memulai HTTP Server pada port {self.port}: {e}")
            self.stop_streaming()

    def _cleanup_conflicting_processes(self) -> None:
        """Menghentikan proses mediamtx dan ffmpeg yang sedang berjalan untuk membebaskan /dev/video0."""
        print("[FFmpegStreamer] Membersihkan proses ffmpeg/mediamtx lama...")
        try:
            subprocess.run(["pkill", "-f", "mediamtx"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-f", "ffmpeg"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
        except Exception as e:
            print(f"[FFmpegStreamer] Peringatan saat pkill: {e}")

    def stop_streaming(self) -> None:
        """Menghentikan HTTP Server, thread pembaca, dan subproses FFmpeg."""
        self.is_running = False
        
        # 1. Hentikan HTTP Server
        if self.http_server:
            try:
                self.http_server.shutdown()
                self.http_server.server_close()
            except Exception:
                pass
            self.http_server = None
            
        # 2. Hentikan Thread Reader
        if self.reader:
            self.reader.is_running = False
            self.reader = None
            
        # 3. Hentikan proses FFmpeg
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
            
        print("[FFmpegStreamer] Stream video dihentikan sepenuhnya.")
