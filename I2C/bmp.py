import time
import board, busio
from adafruit_bme280 import basic as adafruit_bme280
from config import ADDR_BMP, SEA_LEVEL

i2c = busio.I2C(board.SCL, board.SDA)
bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=ADDR_BMP)

def init_bmp280():
    bme.sea_level_pressure = SEA_LEVEL
    print("[BMP] init senzor hum si temp")



def read_temp_hum():
    return bme.temperature, bme.humidity