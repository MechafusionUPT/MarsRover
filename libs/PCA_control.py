
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from constants import *
import time

def angle_to_duty(angle_deg, min_us=MIN_PCA, max_us=MAX_PCA, freq=FREQ_PCA): #POT FI MODIFICATE
    pulse_us = min_us + (angle_deg / 180.0) * (max_us - min_us)
    duty16 = int((pulse_us * 65535 * freq) / 1_000_000)
    return duty16

