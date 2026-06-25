from src.domain.models import JoystickInput
from src.usecases.drive_tank import DriveTankUseCase
from src.usecases.aim_camera import AimCameraUseCase
from src.usecases.play_soundboard import PlaySoundboardUseCase

class RobotController:
    """Controller yang bertugas menerima parameter mentah dari adapter jaringan (CommandPort),
    melakukan parsing/translasi ke objek domain, lalu memicu use case yang sesuai.
    """

    def __init__(
        self,
        drive_tank_usecase: DriveTankUseCase,
        aim_camera_usecase: AimCameraUseCase,
        play_soundboard_usecase: PlaySoundboardUseCase
    ):
        self._drive_tank = drive_tank_usecase
        self._aim_camera = aim_camera_usecase
        self._play_soundboard = play_soundboard_usecase

    def handle_tank_joystick(self, x: float, y: float) -> None:
        """Menangani pergerakan joystick roda tank."""
        try:
            joystick_input = JoystickInput(x=x, y=y)
            self._drive_tank.execute(joystick_input)
        except Exception as e:
            # Di sini kita bisa mengintegrasikan logger yang sesungguhnya
            print(f"[RobotController] Gagal memproses joystick tank: {e}")

    def handle_camera_joystick(self, x: float, y: float) -> None:
        """Menangani pergerakan joystick orientasi servo kamera."""
        try:
            joystick_input = JoystickInput(x=x, y=y)
            self._aim_camera.execute(joystick_input)
        except Exception as e:
            print(f"[RobotController] Gagal memproses joystick kamera: {e}")

    def handle_soundboard(self, sound_name: str) -> None:
        """Menangani permintaan pemutaran soundboard."""
        try:
            self._play_soundboard.execute(sound_name)
        except Exception as e:
            print(f"[RobotController] Gagal memutar soundboard {sound_name}: {e}")
