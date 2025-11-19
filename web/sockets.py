# web/sockets.py

from flask_socketio import emit

from control.motors import set_drive
from I2C.PCA import set_pitch_to, change_pitch_by, reset_pitch
from I2C.PCA import set_grip_to, set_grip, change_grip_by
from I2C.bmp import read_temp_hum


def init_sockets(socketio):

    @socketio.on("connect")
    def on_connect():
        print("[SOCKET] Client conectat", flush=True)
        emit("server.status", {"ok": True})

    @socketio.on("control.move")
    def on_move(data):
        vx = float(data.get("vx", 0.0))
        vy = float(data.get("vy", 0.0))
        sx = float(data.get("sx", 0.0)) # pentru Pitch
        grip = int(data.get("grip", 0)) #setam Grip (True sau False)
        pitch = int(data.get("pitch", 0)) #

        print(f"[SOCKET] vx={vx:.2f} vy={vy:.2f} sx={sx:.2f} grip={grip} pitch={pitch}", flush=True)

        # logica ta de mișcare
        set_drive(vx, vy)
        set_grip(grip)
        change_pitch_by(sx)
        if(pitch):
            reset_pitch()

        emit(
            "telemetry.movement",
            {"vx": vx, "vy": vy, "sx": sx, "grip": grip, "pitch": pitch},
            broadcast=True,
        )
        
    def telemetry_loop():
        print("[SOCKET] telemetry_loop pornit", flush=True)
        while True:
            temp, hum = read_temp_hum()
            socketio.emit(
                "telemetry.sensors",
                {"temp": temp, "hum": hum},
            )
            socketio.sleep(1.0) 

    socketio.start_background_task(telemetry_loop)