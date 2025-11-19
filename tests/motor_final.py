#TEST PENTRU MOTOARE
import time
from config import *
from control.motors import init_motors, set_drive, pwm_cleanup

init_motors()
speed=0.5
while True:
    set_drive(speed,-speed)
    print(1)
    time.sleep(3)
    set_drive(0,0)
    print(2)
    time.sleep(3)
    set_drive(-speed, speed)
    print(3)
    time.sleep(3)

pwm_cleanup()



