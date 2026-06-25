import asyncio
import json
import threading
from typing import Callable
from src.domain.models import JoystickInput
from src.usecases.ports.command_port import CommandPort

# Coba import websockets untuk server WebSocket modern,
# jika tidak tersedia, kita bisa memasangnya nanti atau menggunakan simulasi.
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False


class NetworkReceiver(CommandPort):
    """Implementasi CommandPort menggunakan WebSocket Server.
    Menerima instruksi kendali dalam format JSON dari aplikasi Android.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        
        self.on_tank_joystick = None
        self.on_camera_joystick = None
        self.on_soundboard = None

        self._loop = None
        self._server = None
        self._thread = None
        self._is_running = False

    def start_listening(
        self,
        on_tank_joystick: Callable[[JoystickInput], None],
        on_camera_joystick: Callable[[JoystickInput], None],
        on_soundboard: Callable[[str], None]
    ) -> None:
        """Memulai WebSocket server pada thread terpisah."""
        self.on_tank_joystick = on_tank_joystick
        self.on_camera_joystick = on_camera_joystick
        self.on_soundboard = on_soundboard
        self._is_running = True

        if HAS_WEBSOCKETS:
            self._thread = threading.Thread(target=self._run_async_server, daemon=True)
            self._thread.start()
            print(f"[NetworkReceiver] WebSocket Server berjalan di ws://{self.host}:{self.port}")
        else:
            print("[NetworkReceiver] Paket 'websockets' tidak terdeteksi.")
            print("[NetworkReceiver] Silakan instal dengan `pip install websockets` atau gunakan mode simulasi.")
            self._thread = threading.Thread(target=self._run_simulation_input, daemon=True)
            self._thread.start()

    def _run_async_server(self) -> None:
        """Menjalankan loop event asyncio pada thread ini."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        self._loop.run_until_complete(self._start_server())
        try:
            self._loop.run_forever()
        except asyncio.CancelledError:
            pass
        finally:
            self._loop.close()

    async def _start_server(self) -> None:
        """Inisialisasi server WebSocket."""
        self._server = await websockets.serve(self._handle_connection, self.host, self.port)

    async def _handle_connection(self, websocket, path) -> None:
        """Menangani pesan masuk dari klien WebSocket (aplikasi android)."""
        # print(f"[NetworkReceiver] Klien terhubung dari: {websocket.remote_address}")
        try:
            async for message in websocket:
                if not self._is_running:
                    break
                
                try:
                    payload = json.loads(message)
                    event = payload.get("event")
                    data = payload.get("data")

                    if event == "tank_joystick":
                        x = float(data.get("x", 0.0))
                        y = float(data.get("y", 0.0))
                        if self.on_tank_joystick:
                            self.on_tank_joystick(JoystickInput(x=x, y=y))

                    elif event == "camera_joystick":
                        x = float(data.get("x", 0.0))
                        y = float(data.get("y", 0.0))
                        if self.on_camera_joystick:
                            self.on_camera_joystick(JoystickInput(x=x, y=y))

                    elif event == "soundboard":
                        sound_name = str(data)
                        if self.on_soundboard:
                            self.on_soundboard(sound_name)

                except (json.JSONDecodeError, TypeError, KeyError) as e:
                    # Abaikan payload yang tidak valid agar server tidak crash
                    pass
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"[NetworkReceiver] Error pada koneksi WebSocket: {e}")
        # finally:
        #     print(f"[NetworkReceiver] Klien terputus: {websocket.remote_address}")

    def _run_simulation_input(self) -> None:
        """Menjalankan input simulasi lewat terminal jika 'websockets' tidak ada."""
        print("[NetworkReceiver SIMULASI] Ketik perintah simulasi (misal: 'maju', 'mundur', 'kiri', 'kanan', 'sound horn', 'stop')")
        while self._is_running:
            try:
                cmd = input().strip().lower()
                if not self._is_running:
                    break

                if cmd == "maju":
                    self.on_tank_joystick(JoystickInput(x=0.0, y=1.0))
                elif cmd == "mundur":
                    self.on_tank_joystick(JoystickInput(x=0.0, y=-1.0))
                elif cmd == "kiri":
                    self.on_tank_joystick(JoystickInput(x=-1.0, y=0.0))
                elif cmd == "kanan":
                    self.on_tank_joystick(JoystickInput(x=1.0, y=0.0))
                elif cmd == "stop":
                    self.on_tank_joystick(JoystickInput(x=0.0, y=0.0))
                elif cmd.startswith("sound "):
                    sound = cmd.split(" ")[1]
                    self.on_soundboard(sound)
                else:
                    print("Perintah tidak dikenal. Coba: maju, mundur, kiri, kanan, sound <nama>, stop")
            except (KeyboardInterrupt, EOFError):
                break

    def stop_listening(self) -> None:
        """Menghentikan server WebSocket."""
        self._is_running = False
        if HAS_WEBSOCKETS and self._loop and self._server:
            # Matikan server secara aman di thread asyncio
            self._loop.call_soon_threadsafe(self._server.close)
            # Matikan loop
            for task in asyncio.all_tasks(self._loop):
                self._loop.call_soon_threadsafe(task.cancel)
            self._loop.call_soon_threadsafe(self._loop.stop)
            print("[NetworkReceiver] WebSocket Server dihentikan.")
