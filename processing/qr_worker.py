# processing/qr_worker.py

import time
import threading
import cv2
import numpy as np
from pyzbar.pyzbar import decode as zbar_decode, ZBarSymbol

from cameras import get_ip_frame
from config import (
    QR_TARGET_FPS,
    QR_JPEG_QUALITY,
    QR_EMIT_INTERVAL,
    STREAM_JPEG_QUALITY,
    LOG_QR_DETECTIONS,
)

_qr_lock = threading.Lock()
_qr_last_jpeg = None
_stop = False

def _draw_overlay(frame, boxes, text=None):
    for pts in boxes:
        n = len(pts)
        for i in range(n):
            p1 = tuple(pts[i])
            p2 = tuple(pts[(i + 1) % n])
            cv2.line(frame, p1, p2, (0, 255, 0), 2)


def _qr_loop(socketio):
    """
    Worker QR:
    - ia ultimul frame de la IP camera,
    - face preprocesare simplă,
    - decodează doar cu ZBar,
    - desenează overlay,
    - expune ultimul JPEG pentru stream,
    - emite qr.detected (throttled).
    """
    global _qr_last_jpeg, _stop

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enc_params = [cv2.IMWRITE_JPEG_QUALITY, STREAM_JPEG_QUALITY]

    dt = 1.0 / float(QR_TARGET_FPS)
    next_t = time.time()

    last_text = None
    last_emit = 0.0

    print("[QR] worker pornit", flush=True)

    while not _stop:
        now = time.time()
        if now < next_t:
            time.sleep(next_t - now)
        next_t = max(next_t + dt, time.time())

        # 1. Cadru curent de la IP camera
        frame = get_ip_frame()
        if frame is None:
            continue

        # 2. Preprocesare:
        # grayscale + CLAHE + optional threshold pentru robusteză
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = clahe.apply(gray)

        # ZBar merge și pe grayscale, threshold-ul ajută uneori la contrast
        bw = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 35, 5
        )

        decoded_texts = []
        boxes = []

        # 3. Detectare QR cu ZBar
        for obj in zbar_decode(bw, symbols=[ZBarSymbol.QRCODE]):
            t = obj.data.decode("utf-8", errors="ignore")
            if not t:
                continue
            decoded_texts.append(t)

            pts = [(p.x, p.y) for p in obj.polygon]
            if len(pts) >= 4:
                boxes.append(np.array(pts[:4], dtype=int))
            else:
                x, y, w, h = obj.rect
                boxes.append(
                    np.array(
                        [[x, y], [x + w, y], [x + w, y + h], [x, y + h]],
                        dtype=int,
                    )
                )

        main_text = decoded_texts[0] if decoded_texts else None

        # 4. Overlay pe frame-ul original (nu pe bw)
        if boxes:
            for pts in boxes:
                n = len(pts)
                for i in range(n):
                    p1 = tuple(pts[i])
                    p2 = tuple(pts[(i + 1) % n])
                    cv2.line(frame, p1, p2, (0, 255, 0), 2)

            """if main_text:
            shown = main_text[:80]
            cv2.putText(
                frame,
                shown,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )"""

            # 5. Emit throttled
            now = time.time()
            changed = (main_text != last_text)
            too_old = (now - last_emit) > QR_EMIT_INTERVAL
            if changed or too_old:
                if LOG_QR_DETECTIONS:
                    print(f"[QR] detected: {main_text}", flush=True)
                if socketio is not None:
                    socketio.emit(
                        "qr.detected",
                        {"text": main_text, "ts": now},
                        broadcast=True,
                    )
                last_text = main_text
                last_emit = now

        # 6. JPEG pentru stream_phone_qr.mjpg
        ok, buf = cv2.imencode(".jpg", frame, enc_params)
        if not ok:
            continue

        with _qr_lock:
            _qr_last_jpeg = buf.tobytes()

    print("[QR] worker oprit", flush=True)



def start_qr_worker(socketio):
    t = threading.Thread(target=_qr_loop, args=(socketio,), daemon=True)
    t.start()
    print("[QR] start_qr_worker lansat", flush=True)


def get_qr_jpeg():
    with _qr_lock:
        return _qr_last_jpeg
