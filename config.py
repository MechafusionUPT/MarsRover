# config.py

from pathlib import Path

# BAZĂ PROIECT
BASE_DIR = Path(__file__).resolve().parent

#TEAM DATA
TEAM_NAME= "Mechafusion"

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
IP_CAMERA_URL = "http://10.208.194.3:8080/video"
IP_BUFFERSIZE = 1             # ca să nu acumulezi lag

# QR WORKER
QR_TARGET_FPS = 20          # cât de des procesezi cadrele
QR_JPEG_QUALITY = 70
QR_EMIT_INTERVAL = 5.0        # secunde: cât de des poți retrimite același text

# STREAM MJPEG (OUTPUT)
STREAM_JPEG_QUALITY = 70        # pentru streamul QR cu overlay

# MOTOARE / CONTROL
LEFT_MOT=0
RIGHT_MOT=1
COMPENSATION_LEFT=0
COMPENSATION_RIGHT=0
CHIP=0
PWM_FREQ_HZ=10000
PWM_PERIOD_NS = int (1e9 // PWM_FREQ_HZ)
ENA=12 #GALBEN
ENB=13 #VERDE
IN1=23 #ALBASTRU
IN2=24 #MOV
IN3=5 #ALB
IN4=6 #GRI

#HARDWARE PWM
PWM_PATH = "/sys/class/pwm/pwmchip0"
PWM0 = f"{PWM_PATH}/pwm0"   # GPIO12 -> ENA
PWM1 = f"{PWM_PATH}/pwm1"   # GPIO13 -> ENB

#SERVO
ADDR_PCA=0x41
FREQ_PCA=50
MIN_PCA=500
MAX_PCA=2500

CHINA = 180
channelGrip=12 #gripperServo pe PCA
DEFAULT_GRIP=0 #Default: closed
FACT_GRIP=5
GRIP_CLOSED=0
GRIP_OPEN=40

GOBILDA = 300
channelPitch=0 #pitchServo pe PCA
DEFAULT_PITCH = 10 
FACT_PITCH=10
UP_PITCH=0
DOWN_PITCH=240

#BMP280
ADDR_BMP=0x76
SEA_LEVEL=1013.25

#AMPERMETER
ADDR_AMP=0x40
THRESHOLD_AMP=1700
OVERSHOOT = 10

# DEBUG / LOGGING
DEBUG = True
LOG_QR_DETECTIONS = True
