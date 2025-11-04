#TESTE PENTRU SERVO SI MOTOARE
from MarsRover.libs.utils import clamp
from flask import Flask, render_template, request, jsonify
from MarsRover.libs.i2c_operations import send_sx_grip

#TODO: de modificat

freq_servo=50
freq_motor=1000


#TODO: de modificat
chALeft, chBLeft, chARight, chBRight= 0,0,0,0

def set_drive(vx: float, vy: float):
    k = 1.0
    left  = clamp(vy + k*vx, -1.0, 1.0)
    right = clamp(vy - k*vx, -1.0, 1.0)

# --- CONFIG ---
I2C_BUS_ID = 1
ARDUINO_ADDR = 0x08
PCA_SER_ADDR = 0x40
PCA_MOT_ADDR = 0x41
PCA_FREQ_MOT = 1000
PCA_FREQ_SER = 50

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("indexController.html")

@app.route("/movement", methods=["POST"])
def servo():
    d = request.get_json(silent=True) or {}
    try:
        sx = clamp(d.get("sx", 0.0))
        grip = bool(d.get("grip", False))
        send_sx_grip(sx, ) #TODO
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
