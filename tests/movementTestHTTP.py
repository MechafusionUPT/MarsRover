# TEST PENTRU MOVEMENT PRIN INTERFATA WEB
from flask import Flask, render_template, request, jsonify
from pathlib import Path
from threading import Thread, Event, Lock
#from flask_sock import Sock
from libs.utils import clamp
from pathlib import Path
import time
from constants import *
from libs.motors import *

pwm_setup()

BASE_DIR = Path(__file__).resolve().parents[1]  # MarsRover/
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

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
        pwm_speed(0, vx)
        pwm_speed(1, vy)
        return jsonify(ok=True, vx=vx, vy=vy, sx=sx, grip=grip)
    except Exception as e:
        return jsonify(ok=False, error=f"/movement: {type(e).__name__}: {e}"), 500

@app.route("/api/telemetry")
def api_telemetry():
    try:
        t, h= 0, 0
        #t,h=read_temp_hum()
        return jsonify(ok=True, temp=round(t,2), hum=round(h,2))
    except Exception as e:
        return jsonify(ok=False, error=f"/api/telemetry: {type(e).__name__}: {e}"), 500
    
if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)
