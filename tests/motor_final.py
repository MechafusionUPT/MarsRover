#TEST PENTRU MOTOARE
import time
from constants import *
from libs.motors import *

pwm_setup()


while False:
    pwm_speed(0, -1) 
    pwm_speed(1, 1)
    time.sleep(3)
    pwm_speed(0, 1)
    pwm_speed(1, -1)
    time.sleep(3)
    
pwm_cleanup()
