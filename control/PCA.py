
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
import time
from config import GRIP_CLOSED, GRIP_OPEN, DEFAULT_PITCH, MAX_PITCH, MIN_PITCH, ADDR_PCA, FREQ_PCA, MIN_PCA, MAX_PCA, channelGrip, channelPitch


i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=ADDR_PCA)
pca.frequency = FREQ_PCA
this_angle=DEFAULT_PITCH

def init_servos():
    print("[SERVO] Servo setup complet ")

def _angle_to_duty(angle_deg, min_us=MIN_PCA, max_us=MAX_PCA, freq=FREQ_PCA): #POT FI MODIFICATE
    pulse_us = min_us + (angle_deg / 180.0) * (max_us - min_us)
    duty16 = int((pulse_us * 65535 * freq) / 1_000_000)
    return duty16

def set_grip(s):
    if s:
        pca.channels[channelGrip].duty_cycle = _angle_to_duty(GRIP_CLOSED)
    else:
        pca.channels[channelGrip].duty_cycle = _angle_to_duty(GRIP_OPEN)

def set_pitch(angle):
    pca.channels[channelPitch].duty_cycle = _angle_to_duty(this_angle)