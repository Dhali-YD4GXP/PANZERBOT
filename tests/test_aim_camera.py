import unittest
from unittest.mock import Mock
from src.domain.models import JoystickInput, CameraOrientation
from src.usecases.aim_camera import AimCameraUseCase
from src.usecases.ports.servo_port import ServoPort

class TestAimCameraUseCase(unittest.TestCase):

    def setUp(self):
        self.mock_servo_port = Mock(spec=ServoPort)
        # Setup initial state
        self.mock_servo_port.get_orientation.return_value = CameraOrientation(pan=90.0, tilt=90.0)
        self.usecase = AimCameraUseCase(self.mock_servo_port, max_step=5.0)

    def test_incremental_move_pan_left(self):
        # Joystick didorong ke kiri (x = -1.0)
        # delta_pan = -(-1.0) * 5.0 = +5.0
        # pan baru = 90.0 + 5.0 = 95.0
        # tilt baru = 90.0 + 0 = 90.0
        joystick = JoystickInput(x=-1.0, y=0.0)
        self.usecase.execute(joystick)

        self.mock_servo_port.set_orientation.assert_called_with(
            CameraOrientation(pan=95.0, tilt=90.0)
        )

    def test_incremental_move_tilt_up(self):
        # Joystick didorong ke depan/atas (y = 1.0)
        # delta_tilt = 1.0 * 5.0 = +5.0
        # tilt baru = 90.0 + 5.0 = 95.0
        # pan baru = 90.0 + 0 = 90.0
        joystick = JoystickInput(x=0.0, y=1.0)
        self.usecase.execute(joystick)

        self.mock_servo_port.set_orientation.assert_called_with(
            CameraOrientation(pan=90.0, tilt=95.0)
        )

    def test_deadzone(self):
        # Joystick bernilai sangat kecil di dalam deadzone
        joystick = JoystickInput(x=0.02, y=-0.01)
        self.usecase.execute(joystick)

        # Tidak boleh memanggil set_orientation karena terabaikan oleh deadzone
        self.mock_servo_port.set_orientation.assert_not_called()

    def test_center_camera(self):
        self.usecase.center_camera()
        self.mock_servo_port.set_orientation.assert_called_with(
            CameraOrientation(pan=90.0, tilt=90.0)
        )

if __name__ == "__main__":
    unittest.main()
