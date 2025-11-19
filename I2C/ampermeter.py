import board
import busio
import adafruit_ina219
import time

# Inițializarea magistralei I2C
i2c_bus = busio.I2C(board.SCL, board.SDA)
ina219 = adafruit_ina219.INA219(i2c_bus)
    # Puteți calibra senzorul aici daca aveti nevoie de precizie mai mare
    # De exemplu, pentru a masura pana la 16V si 3.2A: ina219.set_calibration_32V_2A() 


def init_amp():
    print("[AMP] Initializare ampermetru")

while True:
    # Citirea valorilor
    bus_voltage = ina219.bus_voltage        # Tensiunea pe magistrala (Volti)
    shunt_voltage = ina219.shunt_voltage    # Tensiunea pe sunt (Volti)
    current = ina219.current                # Curentul (miliAmperi)
    power = ina219.power                    # Puterea (miliWatti)
    
    # Afișarea rezultatelor
    print("-" * 30)
    print(f"Tensiunea Bus (V): {bus_voltage:0.4f} V")
    print(f"Tensiunea Shunt (mV): {shunt_voltage * 1000:0.4f} mV")
    print(f"Curent (mA): {current:0.4f} mA")
    print(f"Putere (mW): {power:0.4f} mW")
    
    # Așteaptă o secundă înainte de următoarea citire
    time.sleep(1)