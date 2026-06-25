from src.domain.models import JoystickInput, CameraOrientation
from src.usecases.ports.servo_port import ServoPort

class AimCameraUseCase:
    """Use Case untuk mengendalikan servo pan-tilt kamera berdasarkan input joystick.
    Menggunakan kendali tipe inkremental (kecepatan) agar posisi kamera tetap bertahan
    saat joystick dilepas ke posisi netral (tengah).
    """

    def __init__(self, servo_port: ServoPort, max_step: float = 3.0):
        """
        Args:
            servo_port: Driver port untuk mengendalikan servo.
            max_step: Derajat maksimum perubahan sudut per siklus update saat joystick didorong penuh.
        """
        self._servo_port = servo_port
        self._max_step = max_step

    def execute(self, joystick: JoystickInput) -> None:
        """Memperbarui sudut pan-tilt servo secara inkremental berdasarkan input joystick.
        - joystick.x (horizontal) mengendalikan gerakan PAN (kiri/kanan).
        - joystick.y (vertical) mengendalikan gerakan TILT (atas/bawah).
        """
        # Ambil orientasi kamera saat ini
        current = self._servo_port.get_orientation()

        # Lewati pembaruan jika joystick dalam zona toleransi mati (deadzone) kecil
        if abs(joystick.x) < 0.05 and abs(joystick.y) < 0.05:
            return

        # Hitung perubahan sudut berdasarkan nilai joystick
        # Catatan: Gerakan horizontal (x) mengubah PAN, vertikal (y) mengubah TILT
        # Anda bisa mengubah tanda minus/plus di bawah tergantung orientasi fisik servo
        delta_pan = -joystick.x * self._max_step
        delta_tilt = joystick.y * self._max_step

        new_pan = current.pan + delta_pan
        new_tilt = current.tilt + delta_tilt

        # Bentuk objek domain CameraOrientation (secara otomatis membatasi nilai 0.0 s.d 180.0 derajat)
        new_orientation = CameraOrientation(pan=new_pan, tilt=new_tilt)

        # Kirim ke driver servo
        self._servo_port.set_orientation(new_orientation)

    def center_camera(self) -> None:
        """Mengembalikan kamera ke posisi tengah (90 derajat untuk pan dan tilt)."""
        self._servo_port.set_orientation(CameraOrientation(pan=90.0, tilt=90.0))
