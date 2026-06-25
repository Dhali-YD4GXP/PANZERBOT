import sys
import time
from src.adapters.drivers.gpio_motor import GPIOMotorDriver
from src.adapters.drivers.gpio_servo import GPIOServoDriver
from src.adapters.drivers.speaker_driver import SpeakerDriver
from src.adapters.drivers.network_receiver import NetworkReceiver
from src.adapters.drivers.ffmpeg_streamer import FFmpegStreamer

from src.usecases.drive_tank import DriveTankUseCase
from src.usecases.aim_camera import AimCameraUseCase
from src.usecases.play_soundboard import PlaySoundboardUseCase

from src.adapters.controllers.robot_controller import RobotController

def main():
    print("==========================================")
    print("       PANZERBOT RASPBERRY PI BACKEND     ")
    print("==========================================")

    # 1. Inisialisasi Drivers (Hardware & Network Adapters)
    motor_driver = GPIOMotorDriver()
    servo_driver = GPIOServoDriver()
    speaker_driver = SpeakerDriver()
    network_receiver = NetworkReceiver(host="0.0.0.0", port=8765)
    video_streamer = FFmpegStreamer(device="/dev/video0", port=8888)

    # 2. Inisialisasi Use Cases (Logika Aplikasi)
    drive_tank_usecase = DriveTankUseCase(motor_driver)
    aim_camera_usecase = AimCameraUseCase(servo_driver)
    play_soundboard_usecase = PlaySoundboardUseCase(speaker_driver)

    # 3. Inisialisasi Controller
    controller = RobotController(
        drive_tank_usecase=drive_tank_usecase,
        aim_camera_usecase=aim_camera_usecase,
        play_soundboard_usecase=play_soundboard_usecase
    )

    # 4. Hubungkan Adapter Jaringan ke Controller
    print("[Main] Menghubungkan receiver jaringan ke controller...")
    network_receiver.start_listening(
        on_tank_joystick=controller.handle_tank_joystick,
        on_camera_joystick=controller.handle_camera_joystick,
        on_soundboard=controller.handle_soundboard
    )

    print("[Main] Memulai direct video streamer...")
    video_streamer.start_streaming()

    # Kembalikan kamera ke posisi tengah saat startup
    aim_camera_usecase.center_camera()

    print("[Main] Panzerbot Backend siap menerima instruksi.")
    print("Tekan Ctrl+C untuk keluar secara aman.")

    try:
        # Loop utama tetap berjalan menjaga proses tidak mati
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Main] Mematikan Panzerbot Backend secara aman...")
    finally:
        # 5. Cleanup Resources
        network_receiver.stop_listening()
        video_streamer.stop_streaming()
        drive_tank_usecase.stop()
        play_soundboard_usecase.stop()
        
        # Cleanup pin GPIO fisik
        motor_driver.cleanup()
        servo_driver.cleanup()
        print("[Main] Panzerbot Backend berhenti sepenuhnya.")

if __name__ == "__main__":
    main()
