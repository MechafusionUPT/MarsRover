import board
import busio
import struct
from adafruit_bus_device.i2c_device import I2CDevice

# Inițializare bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

#TODO: trebuie modificat, nu mai folosim ARDUINO (direct de la senzor)
# Arduino -> Pi
def read_temp_hum():
    # Așteaptă până busul e disponibil
    while not i2c.try_lock():
        pass
    try:
        with I2CDevice(i2c, ) as device:
            # trimite comanda 0x00
            device.write(bytes([0x00]))
            # citește 8 bytes (2 float-uri)
            data = bytearray(8)
            device.readinto(data)
            temp, hum = struct.unpack('<ff', data)
            return temp, hum
    finally:
        i2c.unlock()


