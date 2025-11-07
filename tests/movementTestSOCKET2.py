import cv2, time, threading, numpy as np
from flask import Response, Flask, render_template
from flask_socketio import SocketIO, emit
from pyzbar.pyzbar import decode as zbar_decode, ZBarSymbol
from pathlib import Path
from libs.motors import *

pwm_setup()
cap0_lock = threading.Lock()
last_jpeg0 = None  # bytes, nu mai stocăm BGR
stop_flag = False

def camera_loop(dev=0, w=640, h=480, fps=60, q=70, drain=2):
    global last_jpeg0, stop_flag
    cap = cv2.VideoCapture(dev, cv2.CAP_V4L2)
    if not cap.isOpened():
        print(f"[CAM] Nu pot deschide /dev/video{dev}")
        return
    # setări „low-latency”
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    cap.set(cv2.CAP_PROP_FPS, fps)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # esențial
    print(f"[CAM] Pornit /dev/video{dev} {w}x{h}@{fps} MJPG")

    # parametri JPEG OpenCV
    enc_params = [cv2.IMWRITE_JPEG_QUALITY, q]

    while not stop_flag:
        # aruncă cadre vechi dacă s-a format backlog
        for _ in range(drain):
            cap.grab()
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.005); continue
        # opțional: mic overlay sau corecții, altfel direct encode
        ok, buf = cv2.imencode('.jpg', frame, enc_params)
        if not ok:
            continue
        with cap0_lock:
            last_jpeg0 = buf.tobytes()

    cap.release()

def gen_frames():
    # doar livrează bytes gata encodați
    while True:
        with cap0_lock:
            b = last_jpeg0
        if b is None:
            time.sleep(0.01); continue
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + b + b'\r\n')

def gen_frames_phone_qr(url, target_fps=12, quality=70):
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print(f"[CAM] Nu pot deschide fluxul IP: {url}")
        return
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    qrdet = cv2.QRCodeDetector()
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    last_text, last_emit = None, 0.0
    enc_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    dt = 1.0/float(target_fps)
    next_t = time.time()

    while True:
        # sincron simplu la target_fps
        now = time.time()
        if now < next_t:
            time.sleep(next_t - now)
        next_t = max(next_t + dt, time.time())

        # aruncă backlogul
        cap.grab(); cap.grab()
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.02); continue

        # detect pe downscale
        small = cv2.resize(frame, (0,0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        retval, info, points, _ = qrdet.detectAndDecodeMulti(small)

        decoded_texts, boxes = [], []
        if retval and info is not None:
            for txt, pts in zip(info, points or []):
                if txt:
                    decoded_texts.append(txt)
                    pts = (pts.reshape(-1,2) * 2.0).astype(int)  # scale back
                    boxes.append(pts)

        if not decoded_texts:
            # fallback ieftin: grayscale + CLAHE + adaptive doar o dată
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = clahe.apply(gray)
            bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 35, 5)
            for obj in zbar_decode(bw, symbols=[ZBarSymbol.QRCODE]):
                t = obj.data.decode('utf-8', errors='ignore')
                if t:
                    decoded_texts.append(t)
                    pts = [(p.x, p.y) for p in obj.polygon]
                    if len(pts) >= 4:
                        boxes.append(np.array(pts[:4], dtype=int))

        # desen minimalist
        for pts in boxes:
            for i in range(len(pts)):
                p1, p2 = tuple(pts[i]), tuple(pts[(i+1) % len(pts)])
                cv2.line(frame, p1, p2, (0,255,0), 2)

        if decoded_texts:
            shown = decoded_texts[0][:80]
            cv2.putText(frame, shown, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            if decoded_texts[0] != last_text or (time.time() - last_emit) > 1.0:
                socketio.emit("qr.detected", {"text": decoded_texts[0], "ts": time.time()}, broadcast=True)
                last_text, last_emit = decoded_texts[0], time.time()

        ok, buf = cv2.imencode(".jpg", frame, enc_params)
        if not ok:
            continue
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n")

BASE_DIR = Path(__file__).resolve().parents[1] 
app = Flask(__name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"))
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


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

    #control motoare
    pwm_speed(0, vx - vy)
    pwm_speed(1, vx + vy)

    #control servo

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
    t_cam = threading.Thread(target=camera_loop, args=(0, 640, 480, 60, 70, 2), daemon=True)
    t_cam.start()
    socketio.run(app, host="0.0.0.0", port=5000)
