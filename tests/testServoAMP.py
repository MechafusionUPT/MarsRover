import board
import busio
import adafruit_ina219
import time
from I2C.PCA import init_servos, set_pitch_to, reset_pitch, set_grip_to, set_grip_amp
from config import DEFAULT_GRIP, GRIP_CLOSED, GRIP_OPEN
from utils import clamp
from I2C.ampermeter import amp_over_threshold, read_amp
from I2C.ampermeter import init_amp

i2c_bus = busio.I2C(board.SCL, board.SDA)
init_amp()
init_servos()


i=1
this_angle = DEFAULT_GRIP
direction = 1

while True:
    set_grip_to(this_angle)
    this_angle = this_angle + direction

    if this_angle >= GRIP_OPEN or this_angle <= GRIP_CLOSED:
        direction = -direction

    if abs(read_amp()) > 2200:
        break
    if i%10==0:
        print(f"Curent (mA): {read_amp():0.4f} mA")
        print("Angle: {this_angle}")
    time.sleep(0.02)
    i = i + 1
