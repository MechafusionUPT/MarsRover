#TEST PENTRU VERIFICARE CONEXIUNE PCA SI SERVO

from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from control.PCA import set_grip, init_servos
import time

init_servos()

while True: 
    set_grip(False)
    time.sleep(3)
    set_grip(True)
    time.sleep(3)