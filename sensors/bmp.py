import time
import board, busio
from adafruit_bme280 import basic as adafruit_bme280
from config import ADDR_BMP

i2c = busio.I2C(board.SCL, board.SDA)

while True:
    print(f"T={bme.temperature:.2f} °C  RH={bme.relative_humidity:.2f}%  P={bme.pressure:.2f} hPa  Alt={bme.altitude:.2f} m")
    time.sleep(1)

def init_bmp280():
    bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=ADDR_BMP)
    bme.sea_level_pressure = 1013.25
    print("[BMP] init senzor hum si temp")

#def read_temp_hum():
    