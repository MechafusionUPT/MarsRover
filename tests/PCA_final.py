#TEST PENTRU VERIFICARE CONEXIUNE PCA SI SERVO

from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from I2C.PCA import init_servos, set_pitch_to, reset_pitch, set_grip_to, GRIP_CLOSED, GRIP_OPEN
import time

init_servos()

while True: 
    set_pitch_to(0)
    #set_grip_to(GRIP_OPEN)
    print("SUS")
    time.sleep(3)
    set_pitch_to(240)
    #set_grip_to(GRIP_CLOSED)
    print("JOS")
    time.sleep(3)
#while True:
#    set_pitch_to()

