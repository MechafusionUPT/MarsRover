import board
import busio
import adafruit_ina219
import time
from config import THRESHOLD_AMP

# Inițializarea magistralei I2C
i2c_bus = busio.I2C(board.SCL, board.SDA)
ina219 = adafruit_ina219.INA219(i2c_bus)
    # Puteți calibra senzorul aici daca aveti nevoie de precizie mai mare
    # De exemplu, pentru a masura pana la 16V si 3.2A: ina219.set_calibration_32V_2A() 


def init_amp():
    print("[AMP] Initializare ampermetru")

def read_amp():
    return ina219.current

def amp_over_threshold():
    return True if ina219.current > THRESHOLD_AMP else False

