#TEST PENTRU MOTOARE
import time
from config import *
from control.motors import init_motors, set_drive, pwm_cleanup, _pwm_speed

init_motors()
speed=0.5
while False:
    _pwm_speed(0, speed)
    _pwm_speed(1, speed)    
    print(1)
    time.sleep(3)
    _pwm_speed(0, 0)
    _pwm_speed(1, 0)
    print(2)
    time.sleep(3)
    _pwm_speed(0, -speed)
    _pwm_speed(1, -speed)
    print(3)
    time.sleep(3)

pwm_cleanup()



