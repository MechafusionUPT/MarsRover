#TEST PENTRU VERIFICARE CONEXIUNE PCA SI SERVO

from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from I2C.PCA import set_grip, init_servos, set_pitch_to, reset_pitch
import time

init_servos()

while True: 
    set_grip(False) #deschis
    print("Deschis")
    time.sleep(3)
    set_grip(True) #inchis
    print("Inchis")
    time.sleep(3)


#while True:
#    set_pitch_to()

