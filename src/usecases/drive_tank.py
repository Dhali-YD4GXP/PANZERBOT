from src.domain.models import JoystickInput, MotorSpeed
from src.usecases.ports.motor_port import MotorPort

class DriveTankUseCase:
    """Use Case untuk mengendalikan pergerakan tank Panzerbot berdasarkan input joystick."""

    def __init__(self, motor_port: MotorPort):
        self._motor_port = motor_port

    def execute(self, joystick: JoystickInput) -> None:
        """Mengonversi input joystick (x, y) menjadi kecepatan motor kiri dan kanan,
        lalu mengirimkannya ke motor port.
        
        Algoritma menggunakan Differential Drive:
        - y mewakili arah maju/mundur (throttle).
        - x mewakili arah belok kiri/kanan (steering).
        """
        # Hitung kecepatan dasar masing-masing motor
        left_speed = joystick.y + joystick.x
        right_speed = joystick.y - joystick.x

        # Normalisasi jika nilai melebihi -1.0 atau 1.0 agar rasio belok tetap terjaga
        max_val = max(abs(left_speed), abs(right_speed))
        if max_val > 1.0:
            left_speed /= max_val
            right_speed /= max_val

        # Buat objek domain MotorSpeed (secara otomatis akan membatasi nilai antara -1.0 dan 1.0)
        motor_speed = MotorSpeed(left=left_speed, right=right_speed)

        # Kirim ke port driver fisik
        self._motor_port.set_speed(motor_speed)

    def stop(self) -> None:
        """Menghentikan tank."""
        self._motor_port.stop()
