#TEST PENTRU MOTOARE
import time
from config import *
from control.motors import *

init_motors()

while False:
    set_drive(1,-1)
    print(1)
    time.sleep(3)
    set_drive(-1, 1)
    print(2)
    time.sleep(3)

pwm_cleanup()



