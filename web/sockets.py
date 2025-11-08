# web/sockets.py

from flask_socketio import emit

from control.motors import set_drive
from control.PCA import set_grip


def init_sockets(socketio):

    @socketio.on("connect")
    def on_connect():
        print("[SOCKET] Client conectat", flush=True)
        emit("server.status", {"ok": True})

    @socketio.on("control.move")
    def on_move(data):
        vx = float(data.get("vx", 0.0))
        vy = float(data.get("vy", 0.0))
        sx = float(data.get("sx", 0.0))   # rezervat, dacă vei folosi yaw/rotire
        grip = int(data.get("grip", 0))

        print(f"[SOCKET] vx={vx:.2f} vy={vy:.2f} sx={sx:.2f} grip={grip}", flush=True)

        # logica ta de mișcare (normalizată în control.motors)
        set_drive(vx, vy)
        set_grip(grip)

        emit(
            "telemetry.movement",
            {"vx": vx, "vy": vy, "sx": sx, "grip": grip},
            broadcast=True,
        )
