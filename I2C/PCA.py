
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
import time
from config import ADDR_PCA, FREQ_PCA, MIN_PCA, MAX_PCA
from config import DEFAULT_PITCH, UP_PITCH, DOWN_PITCH, FACT_PITCH, channelPitch, GOBILDA
from config import GRIP_CLOSED, GRIP_OPEN, DEFAULT_GRIP, FACT_GRIP, channelGrip, CHINA
from config import THRESHOLD_AMP
from utils import clamp
from I2C.ampermeter import amp_over_threshold, read_amp
from config import OVERSHOOT
import threading

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=ADDR_PCA)
pca.frequency = FREQ_PCA

target = DEFAULT_GRIP
this_angle_grip=DEFAULT_GRIP
this_angle_pitch=DEFAULT_PITCH
last = True

grip_lock = threading.Lock()

def init_servos():
    print("[SERVO] Servo setup complet ")

def _angle_to_duty(angle, range_deg, min_us=MIN_PCA, max_us=MAX_PCA):
    if angle < 0: angle = 0
    if angle > range_deg: angle = range_deg
    pulse_us = min_us + (angle / range_deg) * (max_us - min_us)
    period_us = 20000.0
    duty_16bit = int((pulse_us / period_us) * 65535)
    return duty_16bit

def set_pitch_to(angle):
    pca.channels[channelPitch].duty_cycle = _angle_to_duty(clamp(angle, UP_PITCH, DOWN_PITCH), GOBILDA)

def reset_pitch():
        change_pitch_by(DEFAULT_PITCH)

def change_pitch_by(change):
    global this_angle_pitch
    this_angle_pitch = clamp(this_angle_pitch + (float)(change * FACT_PITCH), UP_PITCH, DOWN_PITCH)
    set_pitch_to(this_angle_pitch)

def set_grip_to(angle):
     pca.channels[channelGrip].duty_cycle = _angle_to_duty(clamp(angle, GRIP_CLOSED, GRIP_OPEN), CHINA)

def change_grip_by(change):
    global target
    global this_angle_grip
    target = clamp(this_angle_grip + (float)(change * FACT_GRIP), GRIP_CLOSED, GRIP_OPEN)
    set_grip_amp(target)

def set_grip_amp(s):
    global last
    global target

    if last != s:
        if s:
            target = GRIP_CLOSED 
        else:
            target = GRIP_OPEN
    last = s
    print(target)

BLOCK_DELAY_SEC = 0.05 # 50 milisecunde de curent mare continuu

# Presupunem ca grip_lock este definit la nivel global in acest modul
# BLOCK_DELAY_SEC si OVERSHOOT sunt constante globale

def update_grip():
    start_block_time = 0.0
    
    while True:
        # Accesăm variabilele globale pentru citire/scriere
        global target
        global this_angle_grip
        
        # Citirea curentului nu necesita lock (este o functie IO/senzor)
        current_amp = abs(read_amp())
        is_over_threshold = current_amp > THRESHOLD_AMP
        
        # Citim target si this_angle_grip intr-un bloc protejat
        with grip_lock:
            current_target = target
            current_angle = this_angle_grip
            
        # Logica Mișcării
        if current_target != current_angle:
            
            # Calculam noua pozitie fara lock, folosind current_angle
            if current_target < current_angle:
                new_angle = clamp(current_angle - 1, GRIP_CLOSED, GRIP_OPEN)
            else:
                new_angle = clamp(current_angle + 1, GRIP_CLOSED, GRIP_OPEN)
            
            # Scriem noua pozitie sub protectia lock-ului
            with grip_lock:
                this_angle_grip = new_angle
            
            set_grip_to(new_angle) # set_grip_to doar citeste this_angle_grip
            time.sleep(0.02)
            
            # Logica de detecție a blocării
            if is_over_threshold:
                if start_block_time == 0.0:
                    start_block_time = time.time() 
                
                elif time.time() - start_block_time >= BLOCK_DELAY_SEC:
                    print(f"!!! BLOCARE DETECTATĂ ({current_amp:.2f} > {THRESHOLD_AMP:.2f}) !!!")
                    
                    # Scriem noul target (oprirea) sub protectia lock-ului
                    with grip_lock:
                        if target < this_angle_grip:
                            target = this_angle_grip + OVERSHOOT 
                        else:
                            target = this_angle_grip - OVERSHOOT 
                            
                    start_block_time = 0.0
                    
            else: # Spike scurt de curent sau curent normal
                start_block_time = 0.0
                
        else:
            # Dacă suntem la target, așteptăm pentru a nu consuma resurse.
            time.sleep(0.1)