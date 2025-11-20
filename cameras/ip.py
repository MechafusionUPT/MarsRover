# cameras/ip.py

import cv2
import time
import threading

from config import IP_CAMERA_URL, IP_BUFFERSIZE

_lock = threading.Lock()
_last_frame = None
_stop = False


def _ip_capture_loop(url):
    global _last_frame, _stop

    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print(f"[IP] Nu pot deschide fluxul: {url}", flush=True)
        return

    cap.set(cv2.CAP_PROP_BUFFERSIZE, IP_BUFFERSIZE)
    print(f"[IP] Conectat la {url}", flush=True)

    while not _stop:
        cap.grab()
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.01)
            continue
        with _lock:
            _last_frame = frame

    cap.release()
    print("[IP] capture oprit", flush=True)


def start_ip_capture():
    t = threading.Thread(target=_ip_capture_loop, args=(IP_CAMERA_URL,), daemon=True)
    t.start()
    print("[IP] ip_capture_loop pornit", flush=True)


def get_ip_frame():
    with _lock:
        if _last_frame is None:
            return None
        return _last_frame.copy()
