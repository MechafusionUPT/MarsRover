# config.py

from pathlib import Path

# BAZĂ PROIECT
BASE_DIR = Path(__file__).resolve().parent

# SERVER
HOST = "0.0.0.0"
PORT = 5000
CORS_ALLOWED_ORIGINS = "*"

# CAMERA USB (passthrough MJPEG)
USB_DEVICE = "/dev/video0"      # sau "0" dacă vrei să folosești index și să-l convertești în cod
USB_WIDTH = 1024
USB_HEIGHT = 576
USB_FPS = 30
USB_INPUT_FORMAT = "mjpeg"      # cerut ffmpeg / v4l2
USB_LOG_EVERY_N_FRAMES = 60     # doar pentru debug

# IP CAMERA (telefon)
IP_CAMERA_URL = "http://10.88.133.228:8080/video"
IP_BUFFERSIZE = 1             # ca să nu acumulezi lag

# QR WORKER
QR_TARGET_FPS = 1            # cât de des procesezi cadrele
QR_JPEG_QUALITY = 70
QR_EMIT_INTERVAL = 5.0        # secunde: cât de des poți retrimite același text

# STREAM MJPEG (OUTPUT)
STREAM_JPEG_QUALITY = 70        # pentru streamul QR cu overlay

# MOTOARE / CONTROL
LEFT_MOT=0
RIGHT_MOT=1
COMPENSATION_LEFT=0.4
COMPENSATION_RIGHT=0.4
CHIP=0
PWM_FREQ_HZ=20_000
PWM_PERIOD_NS = int (1e9 // PWM_FREQ_HZ)
ENA=12
ENB=13
IN1=23
IN2=24
IN3=5
IN4=6

#HARDWARE PWM
PWM_PATH = "/sys/class/pwm/pwmchip0"
PWM0 = f"{PWM_PATH}/pwm0"   # GPIO12 -> ENA
PWM1 = f"{PWM_PATH}/pwm1"   # GPIO13 -> ENB

#SERVO
ADDR_PCA=0x40
FREQ_PCA=50
MIN_PCA=500
MAX_PCA=2500

channelGrip=0 #gripperServo pe PCA
GRIP_CLOSED=180
GRIP_OPEN=0

channelPitch=1 #pitchServo pe PCA
DEFAULT_PITCH=90
FACT_PITCH=5
MAX_PITCH=180
MIN_PITCH=0

#BMP280
ADDR_BMP=0x76

# DEBUG / LOGGING
DEBUG = True
LOG_QR_DETECTIONS = True
