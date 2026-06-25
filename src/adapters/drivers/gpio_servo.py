import os
from src.domain.models import CameraOrientation
from src.usecases.ports.servo_port import ServoPort

try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except ImportError:
    HAS_GPIO = False


class GPIOServoDriver(ServoPort):
    """Implementasi ServoPort menggunakan RPi.GPIO untuk servo pan-tilt.
    Menggunakan sinyal PWM standar 50Hz.
    """

    def __init__(
        self,
        pan_pin: int = 27,   # Pin GPIO untuk servo Pan (horizontal)
        tilt_pin: int = 22,  # Pin GPIO untuk servo Tilt (vertikal)
        min_angle: float = 0.0,
        max_angle: float = 180.0,
        # Standard servo duty cycles (biasanya 2.5% s.d 12.5%, atau 5% s.d 10%)
        min_duty: float = 2.5,
        max_duty: float = 12.5
    ):
        self.pan_pin = pan_pin
        self.tilt_pin = tilt_pin
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.min_duty = min_duty
        self.max_duty = max_duty

        self.pwm_pan = None
        self.pwm_tilt = None

        # Posisi awal (tengah / 90 derajat)
        self._current_orientation = CameraOrientation(pan=90.0, tilt=90.0)

        if HAS_GPIO:
            self._setup_gpio()
        else:
            print("[GPIOServoDriver] RPi.GPIO tidak terdeteksi. Berjalan dalam mode SIMULASI.")

    def _setup_gpio(self) -> None:
        # Gunakan sistem penomoran BCM pin jika belum dipanggil oleh driver lain
        try:
            GPIO.setmode(GPIO.BCM)
        except Exception:
            pass
        GPIO.setwarnings(False)

        # Setup pin servo sebagai output
        GPIO.setup(self.pan_pin, GPIO.OUT)
        GPIO.setup(self.tilt_pin, GPIO.OUT)

        # Inisialisasi PWM pada 50Hz
        self.pwm_pan = GPIO.PWM(self.pan_pin, 50)
        self.pwm_tilt = GPIO.PWM(self.tilt_pin, 50)

        # Mulai servo di posisi default (tengah)
        self.pwm_pan.start(self._angle_to_duty(self._current_orientation.pan))
        self.pwm_tilt.start(self._angle_to_duty(self._current_orientation.tilt))
        print("[GPIOServoDriver] Inisialisasi GPIO Servo sukses.")

    def _angle_to_duty(self, angle: float) -> float:
        """Mengonversi derajat (0-180) ke persen duty cycle PWM."""
        angle_range = self.max_angle - self.min_angle
        duty_range = self.max_duty - self.min_duty
        
        # Penskalaan linier
        duty = ((angle - self.min_angle) / angle_range) * duty_range + self.min_duty
        return duty

    def set_orientation(self, orientation: CameraOrientation) -> None:
        """Mengatur sudut servo pan dan tilt."""
        self._current_orientation = orientation

        if HAS_GPIO:
            duty_pan = self._angle_to_duty(orientation.pan)
            duty_tilt = self._angle_to_duty(orientation.tilt)
            
            self.pwm_pan.ChangeDutyCycle(duty_pan)
            self.pwm_tilt.ChangeDutyCycle(duty_tilt)
        else:
            print(f"[GPIO Servo SIMULASI] Sudut Kamera -> Pan: {orientation.pan:.1f}°, Tilt: {orientation.tilt:.1f}°")

    def get_orientation(self) -> CameraOrientation:
        """Mendapatkan orientasi sudut pan dan tilt kamera saat ini."""
        return self._current_orientation

    def cleanup(self) -> None:
        """Menghentikan PWM servo."""
        if HAS_GPIO:
            if self.pwm_pan:
                self.pwm_pan.stop()
            if self.pwm_tilt:
                self.pwm_tilt.stop()
            GPIO.cleanup([self.pan_pin, self.tilt_pin])
            print("[GPIOServoDriver] GPIO Servo cleanup selesai.")
