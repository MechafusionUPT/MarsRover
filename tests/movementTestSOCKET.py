from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
from pathlib import Path
from libs.motors import *
import cv2
import time
import threading
from pyzbar.pyzbar import decode as zbar_decode, ZBarSymbol
import numpy as np

cap0_lock = threading.Lock()

last_frame0 = None


pwm_setup()
qr_det = cv2.QRCodeDetector()

def camera_loop(dev=2):
    global last_frame0
    cap = cv2.VideoCapture(dev, cv2.CAP_V4L2)
    if not cap.isOpened():
        print(f"[CAM] Nu pot deschide /dev/video{dev}")
        return
    # 640x480@20; încearcă MJPG (coment-ează dacă dă eroare)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 60)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    print(f"[CAM] Pornit /dev/video{dev}")

    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.01); continue
        with cap0_lock:
            last_frame0 = frame


def gen_frames():
    while True:
        with cap0_lock:
            frame = None if last_frame0 is None else last_frame0.copy()
        if frame is None: 
            time.sleep(0.01); continue
        ok, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if not ok: continue
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buf.tobytes() + b'\r\n')

def gen_frames_phone_qr(url="http://192.168.1.35:8080/video"):
    # detector OpenCV (multi)
    qrdet = cv2.QRCodeDetector()
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print(f"[CAM] Nu pot deschide fluxul IP: {url}")
        return

    last_text = None
    last_emit = 0.0
    last_frame_t = 0.0
    target_dt = 1.0 / 12.0   # ~12 fps procesare, suficient pentru QR

    while True:
        # throttling simplu
        now = time.time()
        if now - last_frame_t < target_dt:
            time.sleep(0.005)
            continue
        last_frame_t = now

        ok, frame = cap.read()
        if not ok:
            time.sleep(0.05)
            continue

        # pre-procesare: grayscale + CLAHE + threshold (ajută enorm)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        # binarizare adaptivă (robust la lumină neuniformă)
        bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 35, 5)

        decoded_texts = []
        boxes = []

        # 1) OpenCV detectAndDecodeMulti (dacă prinde, excelent)
        try:
            retval, infos, points, _ = qrdet.detectAndDecodeMulti(frame)
            if retval and infos is not None:
                for txt, pts in zip(infos, points or []):
                    if txt:
                        decoded_texts.append(txt)
                        boxes.append(pts.reshape(-1, 2).astype(int))
        except Exception:
            pass

        # 2) Fallback ZBar pe imagine binarizată (de obicei prinde ce scapă OpenCV)
        if not decoded_texts:
            try:
                for obj in zbar_decode(bw, symbols=[ZBarSymbol.QRCODE]):
                    txt = obj.data.decode('utf-8', errors='ignore')
                    if txt:
                        decoded_texts.append(txt)
                        # zbar dă polygon/bbox în coordonate; desenăm poligonul
                        pts = [(p.x, p.y) for p in obj.polygon]
                        if len(pts) >= 4:
                            boxes.append(np.array(pts[:4], dtype=int))
                        else:
                            x, y, w, h = obj.rect
                            boxes.append(np.array([[x,y],[x+w,y],[x+w,y+h],[x,y+h]], dtype=int))
            except Exception:
                pass

        # desen + emit
        if boxes:
            for pts in boxes:
                for i in range(len(pts)):
                    p1, p2 = tuple(pts[i]), tuple(pts[(i+1) % len(pts)])
                    cv2.line(frame, p1, p2, (0, 255, 0), 2)

        if decoded_texts:
            shown = decoded_texts[0][:80]
            cv2.putText(frame, shown, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # emite la max ~1 Hz sau la schimbare
            if (decoded_texts[0] != last_text) or (now - last_emit > 1.0):
                socketio.emit("qr.detected",
                              {"text": decoded_texts[0], "ts": now},
                              broadcast=True)
                last_text = decoded_texts[0]
                last_emit = now

        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if not ok:
            continue
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n")

BASE_DIR = Path(__file__).resolve().parents[1] 
app = Flask(__name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

@app.route("/")
def index():
    return render_template("indexSOCKET.html")

@socketio.on("connect")
def on_connect():
    print("Client conectat")
    emit("server.status", {"ok": True})

@socketio.on("control.move")
def on_move(data):
    vx = float(data.get("vx", 0))
    vy = float(data.get("vy", 0))
    sx = float(data.get("sx", 0))
    grip = int(data.get("grip", 0))

    print(f"vx={vx:.2f} vy={vy:.2f} sx={sx:.2f} grip={grip}")
    # aici pui controlul motoarelor: drive(vx, vy, sx, grip)
    pwm_speed(0, vx - vy)
    pwm_speed(1, vx + vy)

    emit("telemetry.movement", {"vx": vx, "vy": vy, "sx": sx, "grip": grip}, broadcast=True)


@app.route('/stream.mjpg')
def stream_mjpg():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stream_phone_qr.mjpg')
def stream_phone_qr():
    return Response(gen_frames_phone_qr(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    # /dev/video0 -> stream.mjpg
    t0 = threading.Thread(target=camera_loop, args=(0,), daemon=True)
    # /dev/video2 -> stream_qr.mjpg
    t0.start()
    socketio.run(app, host="0.0.0.0", port=5000)
