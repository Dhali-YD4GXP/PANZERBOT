from dataclasses import dataclass

@dataclass(frozen=True)
class JoystickInput:
    """Representasi input joystick dari aplikasi pengendali.
    x dan y bernilai antara -1.0 sampai 1.0.
    """
    x: float
    y: float

    def __post_init__(self):
        # Validasi batas nilai
        object.__setattr__(self, 'x', max(-1.0, min(1.0, self.x)))
        object.__setattr__(self, 'y', max(-1.0, min(1.0, self.y)))


@dataclass(frozen=True)
class MotorSpeed:
    """Representasi kecepatan motor kiri dan kanan.
    Nilai berkisar antara -1.0 (mundur penuh) sampai 1.0 (maju penuh).
    Nilai 0.0 melambangkan motor berhenti.
    """
    left: float
    right: float

    def __post_init__(self):
        # Validasi batas nilai
        object.__setattr__(self, 'left', max(-1.0, min(1.0, self.left)))
        object.__setattr__(self, 'right', max(-1.0, min(1.0, self.right)))


@dataclass(frozen=True)
class CameraOrientation:
    """Representasi sudut pan dan tilt kamera (dalam derajat).
    Umumnya berkisar antara 0 sampai 180 derajat.
    """
    pan: float
    tilt: float

    def __post_init__(self):
        # Validasi batas nilai sudut servo
        object.__setattr__(self, 'pan', max(0.0, min(180.0, self.pan)))
        object.__setattr__(self, 'tilt', max(0.0, min(180.0, self.tilt)))
