import cv2, time, threading, numpy as np
from flask import Response, Flask, render_template
from flask_socketio import SocketIO, emit
from pyzbar.pyzbar import decode as zbar_decode, ZBarSymbol
from pathlib import Path
from libs.motors import *
import subprocess

pwm_setup()

cap0_lock = threading.Lock()
last_jpeg0 = None
stop_flag = False

ip_frame_lock = threading.Lock()
ip_last_frame = None

qr_lock = threading.Lock()
qr_last_jpeg = None


def camera_loop(dev, w, h, fps):
    global last_jpeg0, stop_flag

    if isinstance(dev, int):
        dev_path = f"/dev/video{dev}"
    else:
        dev_path = dev

    cmd = [
        "ffmpeg",
        "-hide_banner", "-loglevel", "error",
        "-f", "v4l2",
        "-input_format", "mjpeg",
        "-video_size", f"{w}x{h}",
        "-framerate", str(fps),
        "-i", dev_path,
        "-c:v", "copy",
        "-f", "mjpeg",
        "pipe:1"
    ]

    print("[CAM] Pornesc ffmpeg passthrough MJPEG:", " ".join(cmd), flush=True)

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0
        )
    except FileNotFoundError:
        print("[CAM] ffmpeg nu este instalat", flush=True)
        return

    SOI = b"\xff\xd8"
    EOI = b"\xff\xd9"
    buf = b""

    while not stop_flag:
        chunk = proc.stdout.read(4096)
        if not chunk:
            if proc.poll() is not None:
                err = proc.stderr.read().decode(errors="ignore")
                print(f"[CAM] ffmpeg s-a oprit, code={proc.returncode}", flush=True)
                if err:
                    print("[CAM ERR]", err, flush=True)
                break
            continue

        buf += chunk

        while True:
            soi = buf.find(SOI)
            if soi == -1:
                buf = buf[-3:]
                break
            eoi = buf.find(EOI, soi + 2)
            if eoi == -1:
                buf = buf[soi:]
                break

            frame = buf[soi:eoi+2]
            buf = buf[eoi+2:]

            with cap0_lock:
                last_jpeg0 = frame

    try:
        proc.terminate()
    except Exception:
        pass
    print("[CAM] Passthrough MJPEG oprit", flush=True)


def ip_capture_loop(url):
    global ip_last_frame

    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print(f"[IP] Nu pot deschide fluxul IP: {url}", flush=True)
        return

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    print(f"[IP] Conectat la {url}", flush=True)

    while True:
        cap.grab()
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.001)
            continue

        with ip_frame_lock:
            ip_last_frame = frame


def qr_worker(target_fps=30, quality=50):
    global qr_last_jpeg

    qrdet = cv2.QRCodeDetector()
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enc_params = [cv2.IMWRITE_JPEG_QUALITY, quality]

    last_text = None
    last_emit = 0.0

    dt = 1.0 / float(target_fps)
    next_t = time.time()

    while True:
        now = time.time()
        if now < next_t:
            time.sleep(next_t - now)
        next_t = max(next_t + dt, time.time())

        with ip_frame_lock:
            frame = None if ip_last_frame is None else ip_last_frame.copy()
        if frame is None:
            continue

        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        retval, infos, points, _ = qrdet.detectAndDecodeMulti(small)

        decoded_texts, boxes = [], []

        if retval and infos is not None:
            for txt, pts in zip(infos, points or []):
                if txt:
                    decoded_texts.append(txt)
                    pts = (pts.reshape(-1, 2) * 2.0).astype(int)
                    boxes.append(pts)

        if not decoded_texts:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = clahe.apply(gray)
            bw = cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 35, 5
            )
            for obj in zbar_decode(bw, symbols=[ZBarSymbol.QRCODE]):
                t = obj.data.decode('utf-8', errors='ignore')
                if t:
                    decoded_texts.append(t)
                    pts = [(p.x, p.y) for p in obj.polygon]
                    if len(pts) >= 4:
                        boxes.append(np.array(pts[:4], dtype=int))

        for pts in boxes:
            for i in range(len(pts)):
                p1, p2 = tuple(pts[i]), tuple(pts[(i + 1) % len(pts)])
                cv2.line(frame, p1, p2, (0, 255, 0), 2)

        if decoded_texts:
            shown = decoded_texts[0][:80]
            cv2.putText(frame, shown, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            if decoded_texts[0] != last_text or (time.time() - last_emit) > 1.0:
                socketio.emit(
                    "qr.detected",
                    {"text": decoded_texts[0], "ts": time.time()},
                    broadcast=True
                )
                last_text = decoded_texts[0]
                last_emit = time.time()

        ok, buf = cv2.imencode(".jpg", frame, enc_params)
        if not ok:
            continue

        with qr_lock:
            qr_last_jpeg = buf.tobytes()


def gen_frames():
    while True:
        with cap0_lock:
            b = last_jpeg0
        if b is None:
            time.sleep(0.001)
            continue
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + b + b"\r\n")


def gen_frames_phone_qr():
    while True:
        with qr_lock:
            b = qr_last_jpeg
        if b is None:
            time.sleep(0.001)
            continue
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + b + b"\r\n")


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
    print("Client conectat", flush=True)
    emit("server.status", {"ok": True})


@socketio.on("control.move")
def on_move(data):
    vx = float(data.get("vx", 0))
    vy = float(data.get("vy", 0))
    sx = float(data.get("sx", 0))
    grip = int(data.get("grip", 0))

    print(f"vx={vx:.2f} vy={vy:.2f} sx={sx:.2f} grip={grip}", flush=True)

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
    print("[MAIN] Pornesc background tasks", flush=True)

    threading.Thread(target=camera_loop, args=(0, 320, 240, 30), daemon=True).start()
    threading.Thread(target=ip_capture_loop, args=("http://10.146.163.191:8080/video",), daemon=True).start()
    threading.Thread(target=qr_worker, args=(12, 70), daemon=True).start()

    print("[MAIN] Pornesc serverul pe 0.0.0.0:5000", flush=True)
    socketio.run(app, host="0.0.0.0", port=5000)
