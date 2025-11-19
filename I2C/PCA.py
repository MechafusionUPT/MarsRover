
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
import time
from config import ADDR_PCA, FREQ_PCA, MIN_PCA, MAX_PCA
from config import DEFAULT_PITCH, MAX_PITCH, MIN_PITCH, FACT_PITCH, channelPitch
from config import GRIP_CLOSED, GRIP_OPEN, DEFAULT_GRIP, FACT_GRIP, channelGrip
from utils import clamp

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=ADDR_PCA)
pca.frequency = FREQ_PCA

this_angle_grip=DEFAULT_GRIP
this_angle_pitch=DEFAULT_PITCH

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

def set_grip_to(angle):
     pca.channels[channelGrip].duty_cycle = _angle_to_duty(clamp(angle, GRIP_CLOSED, GRIP_OPEN))

def change_grip_by(change):
    global this_angle_grip
    this_angle_grip = clamp(this_angle_grip + (float)(change * FACT_GRIP), GRIP_CLOSED, GRIP_OPEN)
    set_pitch_to(this_angle_grip)

def set_pitch_to(angle):
    pca.channels[channelPitch].duty_cycle = _angle_to_duty(clamp(angle, GRIP_CLOSED, GRIP_OPEN))

def reset_pitch():
        change_pitch_by(DEFAULT_PITCH)

def change_pitch_by(change):
    global this_angle_pitch
    this_angle_pitch = clamp(this_angle_pitch + (float)(change * FACT_PITCH), MIN_PITCH, MAX_PITCH)
    set_pitch_to(this_angle_pitch)