import unittest
from unittest.mock import Mock
from src.domain.models import JoystickInput, MotorSpeed
from src.usecases.drive_tank import DriveTankUseCase
from src.usecases.ports.motor_port import MotorPort

class TestDriveTankUseCase(unittest.TestCase):

    def setUp(self):
        # Buat mock untuk MotorPort agar tidak menyentuh GPIO fisik
        self.mock_motor_port = Mock(spec=MotorPort)
        self.usecase = DriveTankUseCase(self.mock_motor_port)

    def test_forward(self):
        # Joystick didorong lurus ke depan
        joystick = JoystickInput(x=0.0, y=1.0)
        self.usecase.execute(joystick)
        
        # Kecepatan kiri & kanan harus maksimal (1.0, 1.0)
        self.mock_motor_port.set_speed.assert_called_with(
            MotorSpeed(left=1.0, right=1.0)
        )

    def test_backward(self):
        # Joystick didorong lurus ke belakang
        joystick = JoystickInput(x=0.0, y=-1.0)
        self.usecase.execute(joystick)
        
        # Kecepatan kiri & kanan harus maksimal mundur (-1.0, -1.0)
        self.mock_motor_port.set_speed.assert_called_with(
            MotorSpeed(left=-1.0, right=-1.0)
        )

    def test_spin_right(self):
        # Joystick didorong penuh ke kanan (tanpa maju/mundur)
        joystick = JoystickInput(x=1.0, y=0.0)
        self.usecase.execute(joystick)
        
        # Tank harus berputar ke kanan di tempat (kiri maju, kanan mundur)
        self.mock_motor_port.set_speed.assert_called_with(
            MotorSpeed(left=1.0, right=-1.0)
        )

    def test_curve_turn(self):
        # Joystick didorong serong kanan-depan
        joystick = JoystickInput(x=0.5, y=0.5)
        self.usecase.execute(joystick)
        
        # left = 0.5 + 0.5 = 1.0
        # right = 0.5 - 0.5 = 0.0
        # Normalisasi: max_val = 1.0 (tidak berubah)
        self.mock_motor_port.set_speed.assert_called_with(
            MotorSpeed(left=1.0, right=0.0)
        )

    def test_stop(self):
        self.usecase.stop()
        self.mock_motor_port.stop.assert_called_once()

if __name__ == "__main__":
    unittest.main()
