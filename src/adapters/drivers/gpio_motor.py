import os
import sys
from src.domain.models import MotorSpeed
from src.usecases.ports.motor_port import MotorPort

# Coba import GPIO, jika gagal gunakan mock simulator
try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except ImportError:
    HAS_GPIO = False


class GPIOMotorDriver(MotorPort):
    """Implementasi MotorPort menggunakan driver hardware L298N via RPi.GPIO."""

    def __init__(
        self,
        ena_pin: int = 12,  # PWM motor kiri
        in1_pin: int = 5,   # Arah motor kiri 1
        in2_pin: int = 6,   # Arah motor kiri 2
        enb_pin: int = 13,  # PWM motor kanan
        in3_pin: int = 16,  # Arah motor kanan 1
        in4_pin: int = 20,  # Arah motor kanan 2
        frequency: int = 1000
    ):
        self.ena = ena_pin
        self.in1 = in1_pin
        self.in2 = in2_pin
        self.enb = enb_pin
        self.in3 = in3_pin
        self.in4 = in4_pin
        self.freq = frequency

        self.pwm_left = None
        self.pwm_right = None

        if HAS_GPIO:
            self._setup_gpio()
        else:
            print("[GPIOMotorDriver] RPi.GPIO tidak terdeteksi. Berjalan dalam mode SIMULASI.")

    def _setup_gpio(self) -> None:
        # Gunakan sistem penomoran BCM pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup pin arah sebagai output
        for pin in [self.in1, self.in2, self.in3, self.in4]:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        # Setup pin Enable sebagai output untuk PWM
        GPIO.setup(self.ena, GPIO.OUT)
        GPIO.setup(self.enb, GPIO.OUT)

        # Inisialisasi PWM pada pin ENA dan ENB
        self.pwm_left = GPIO.PWM(self.ena, self.freq)
        self.pwm_right = GPIO.PWM(self.enb, self.freq)

        # Mulai PWM dengan duty cycle 0 (berhenti)
        self.pwm_left.start(0)
        self.pwm_right.start(0)
        print("[GPIOMotorDriver] Inisialisasi GPIO L298N sukses.")

    def set_speed(self, speed: MotorSpeed) -> None:
        """Mengatur kecepatan dan arah motor kiri & kanan.
        Speed berkisar -1.0 s.d 1.0.
        """
        # Konversi ke persen duty cycle (0 sampai 100)
        left_dc = abs(speed.left) * 100
        right_dc = abs(speed.right) * 100

        if HAS_GPIO:
            # 1. Kontrol Motor Kiri
            if speed.left > 0:
                GPIO.output(self.in1, GPIO.HIGH)
                GPIO.output(self.in2, GPIO.LOW)
            elif speed.left < 0:
                GPIO.output(self.in1, GPIO.LOW)
                GPIO.output(self.in2, GPIO.HIGH)
            else:
                GPIO.output(self.in1, GPIO.LOW)
                GPIO.output(self.in2, GPIO.LOW)
            self.pwm_left.ChangeDutyCycle(left_dc)

            # 2. Kontrol Motor Kanan
            if speed.right > 0:
                GPIO.output(self.in3, GPIO.HIGH)
                GPIO.output(self.in4, GPIO.LOW)
            elif speed.right < 0:
                GPIO.output(self.in3, GPIO.LOW)
                GPIO.output(self.in4, GPIO.HIGH)
            else:
                GPIO.output(self.in3, GPIO.LOW)
                GPIO.output(self.in4, GPIO.LOW)
            self.pwm_right.ChangeDutyCycle(right_dc)
        else:
            # Print log untuk simulasi jika tidak ada GPIO
            left_dir = "MAJU" if speed.left > 0 else ("MUNDUR" if speed.left < 0 else "DIAM")
            right_dir = "MAJU" if speed.right > 0 else ("MUNDUR" if speed.right < 0 else "DIAM")
            print(f"[GPIO Motor SIMULASI] Kiri: {left_dir} ({left_dc:.1f}%), Kanan: {right_dir} ({right_dc:.1f}%)")

    def stop(self) -> None:
        """Menghentikan semua motor."""
        if HAS_GPIO:
            GPIO.output(self.in1, GPIO.LOW)
            GPIO.output(self.in2, GPIO.LOW)
            GPIO.output(self.in3, GPIO.LOW)
            GPIO.output(self.in4, GPIO.LOW)
            self.pwm_left.ChangeDutyCycle(0)
            self.pwm_right.ChangeDutyCycle(0)
        else:
            print("[GPIO Motor SIMULASI] STOP ALL MOTORS")

    def cleanup(self) -> None:
        """Clean up GPIO resource."""
        self.stop()
        if HAS_GPIO:
            if self.pwm_left:
                self.pwm_left.stop()
            if self.pwm_right:
                self.pwm_right.stop()
            GPIO.cleanup([self.ena, self.in1, self.in2, self.enb, self.in3, self.in4])
            print("[GPIOMotorDriver] GPIO cleanup selesai.")
