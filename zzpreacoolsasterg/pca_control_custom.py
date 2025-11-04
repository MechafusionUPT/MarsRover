#NU
import adafruit_pca9685
from smbus2 import SMBus
from threading import Lock
from MarsRover.libs.utils import clamp
import time

# --- bus unic + lock ---
_BUS_ID = 1
_bus = SMBus(_BUS_ID)
_i2c_lock = Lock()

# registre PCA9685
_MODE1, _PRESCALE, _LED0_ON_L = 0x00, 0xFE, 0x06


class PCA:
    def __init__(self, addr: int):
        self.addr = addr
        self._init_mode()

    def _w_block(self, reg, data):
        with _i2c_lock:
            _bus.write_i2c_block_data(self.addr, reg, data)

    def _w_byte(self, reg, val):
        with _i2c_lock:
            _bus.write_byte_data(self.addr, reg, val)

    def _r_byte(self, reg):
        with _i2c_lock:
            return _bus.read_byte_data(self.addr, reg)

    def _init_mode(self):
        # MODE1 = 0x00 (reset soft)
        self._w_byte(_MODE1, 0x00)
        time.sleep(0.005)
        # auto-increment ON
        old = self._r_byte(_MODE1)
        self._w_byte(_MODE1, (old & 0xEF) | 0xA1)

    def set_freq(self, hz: float):
        hz = float(hz)
        prescale = int(round(25_000_000/(4096*hz)) - 1)
        prescale = int(clamp(prescale, 3, 255))
        old = self._r_byte(_MODE1)
        # sleep
        self._w_byte(_MODE1, (old & 0x7F) | 0x10)
        self._w_byte(_PRESCALE, prescale)
        # wake + auto-inc
        self._w_byte(_MODE1, old & 0xEF)
        time.sleep(0.005)
        self._w_byte(_MODE1, (old & 0xEF) | 0xA1)

    def set_pwm(self, ch: int, on: int, off: int):
        ch = int(ch)
        base = _LED0_ON_L + 4*ch
        self._w_block(base, [on & 0xFF, on>>8, off & 0xFF, off>>8])

    def set_duty(self, ch, duty):
        duty = clamp(int(duty), 0, 4095)
        self.set_pwm(ch, 0, duty)

    def motor(self, chA, chB, v):
        v = clamp(float(v), -1.0, 1.0)
        pwm = int(abs(v)*4095)
        self.set_duty(chA, pwm if v > 0 else 0)
        self.set_duty(chB, pwm if v < 0 else 0)

    def servo_deg(self, ch: int, deg: float):
        """50 Hz: 1.0–2.0 ms => 0–180°."""
        deg = clamp(float(deg), 0.0, 180.0)
        us = 1000.0 + (deg/180.0)*1000.0      # 1000..2000 µs
        off = int((us/20000.0) * 4095.0)      # 20ms perioadă la 50Hz
        self.set_pwm(ch, 0, off)


