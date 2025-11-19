from control.motors import init_motors, _pwm_speed
import time
init_motors()

_pwm_speed(0, 0.5)
_pwm_speed(1, 0.5)
time.sleep(1)
_pwm_speed(0,0)
_pwm_speed(1,0)
