#TEST PENTRU VERIFICARE CONEXIUNE PCA SI SERVO

from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from libs.PCA_control import angle_to_duty
from constants import *
import time

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=ADDR_PCA)
pca.frequency = FREQ_PCA


while True: 
    pca.channels[channelPitch].duty_cycle = angle_to_duty(0)
    pca.channels[channelGrip].duty_cycle = angle_to_duty(0)
    time.sleep(3)
    pca.channels[channelPitch].duty_cycle = angle_to_duty(180)
    pca.channels[channelGrip].duty_cycle = angle_to_duty(180)
    time.sleep(3)