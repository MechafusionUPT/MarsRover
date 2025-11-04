import os
from libs.utils import clamp
from constants import *
import lgpio

h = None
_period_ns = PWM_PERIOD_NS

def _write(path: str, value) -> None:
    with open(path, "w") as f:
        f.write(str(value))

def _export_pwm():
    # export doar dacă nu sunt deja exportate
    for idx, p in ((0, PWM0), (1, PWM1)):
        if not os.path.isdir(p):
            _write(f"{PWM_PATH}/export", idx)

def pwm_setup():
    global h, _period_ns
    # deschide chip GPIO și setează direcțiile
    if h is None:
        h = lgpio.gpiochip_open(CHIP)
        for pin in (IN1, IN2, IN3, IN4):
            lgpio.gpio_claim_output(h, pin)

    # exportează canalele PWM
    _export_pwm()

    # dezactivează înainte de configurare
    for p in (PWM0, PWM1):
        en = f"{p}/enable"
        if os.path.exists(en):
            try: _write(en, 0)
            except PermissionError: pass  # deja 0 sau fără drepturi, ignori

    # setează period și duty=0, apoi enable
    for p in (PWM0, PWM1):
        _write(f"{p}/period", _period_ns)
        _write(f"{p}/duty_cycle", 0)
        _write(f"{p}/enable", 1)

def _set_dir_left(fwd: bool):
    # L298N: IN1/IN2 = direcție motor stânga
    lgpio.gpio_write(h, IN1, 1 if fwd else 0)
    lgpio.gpio_write(h, IN2, 0 if fwd else 1)

def _set_dir_right(fwd: bool):
    # L298N: IN3/IN4 = direcție motor dreapta
    lgpio.gpio_write(h, IN3, 1 if fwd else 0)
    lgpio.gpio_write(h, IN4, 0 if fwd else 1)

def _set_duty(channel: int, duty01: float):
    # duty01 în [0..1]; duty_cycle în ns
    duty01 = clamp(duty01, 0.0, 1.0)
    dc = int(_period_ns * duty01)
    path = PWM0 if channel == 0 else PWM1
    _write(f"{path}/duty_cycle", dc)

def pwm_speed(channel: int, power: float):
    """
    channel: 0=stânga (ENA/GPIO12), 1=dreapta (ENB/GPIO13)
    power:   [-1..1] semn=sens, modul=viteză
    """
    p = clamp(power, -1.0, 1.0)
    # deadband mic să eviți bâzâitul la aproape zero
    if abs(p) < 0.02:
        p = 0.0

    if channel == 0:
        _set_dir_left(p >= 0.0)
        comp=COMPENSATION_LEFT
    elif channel == 1:
        _set_dir_right(p >= 0.0)
        comp=COMPENSATION_RIGHT
    else:
        raise ValueError("channel trebuie să fie 0 sau 1")

    _set_duty(channel, abs(p)+comp)

def pwm_cleanup():
    try:
        for p in (PWM0, PWM1):
            _write(f"{p}/duty_cycle", 0)
            _write(f"{p}/enable", 0)
    finally:
        global h
        if h is not None:
            lgpio.gpiochip_close(h)
            h = None
