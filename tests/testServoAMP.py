import board
import busio
import adafruit_ina219
import time
from I2C.PCA import set_grip, init_servos, set_pitch_to, reset_pitch, set_grip_to
from config import DEFAULT_GRIP, GRIP_CLOSED, GRIP_OPEN
from utils import clamp


i2c_bus = busio.I2C(board.SCL, board.SDA)
ina219 = adafruit_ina219.INA219(i2c_bus)
init_servos()

this_angle = DEFAULT_GRIP
direction = 1
while True:
    set_grip_to(this_angle)
    this_angle = this_angle + direction

    if this_angle == GRIP_OPEN or this_angle == GRIP_CLOSED:
        direction = -direction
    
    print(f"Curent (mA): {ina219.current:0.4f} mA")
    print("Angle: {this_angle}")
    time.sleep(0.5)