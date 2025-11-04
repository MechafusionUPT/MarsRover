# roverTest.py
from flask import Flask, render_template, request, jsonify
from libs.utils import clamp
from libs.i2c_operations import read_temp_hum, send_vx_vy, send_sx_grip
import smbus
import struct 


# --- CONFIG ---
I2C_BUS_ID = 1
ARDUINO_ADDR = 0x08
PCA_SER_ADDR = 0x41
PCA_MOT_ADDR = 0x40
PCA_FREQ_MOT = 10000
PCA_FREQ_SER = 50



app = Flask(__name__)


@app.route("/")
def index():
    return render_template("indexController.html")

@app.route("/movement", methods=["POST"])
def movement():
    d = request.get_json(silent=True) or {}
    try:
        vx = float(clamp(d.get("vx", 0.0)))
        vy = float(clamp(d.get("vy", 0.0)))
        sx = float(clamp(d.get("sx", 0.0)))
        grip = bool(d.get("grip", False))
        
        return jsonify(ok=True)
    except Exception as e:
        # returnează eroarea pentru debug rapid în UI
        return jsonify(ok=False, error=f"/movement: {type(e).__name__}: {e}"), 500

@app.route("/api/telemetry")
def api_telemetry():
    try:
        t,h=read_temp_hum()
        return jsonify(ok=True, temp=round(t,2), hum=round(h,2))
    except Exception as e:
        return jsonify(ok=False, error=f"/api/telemetry: {type(e).__name__}: {e}"), 500
    
if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)
