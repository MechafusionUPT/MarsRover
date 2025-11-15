# cameras/usb.py
#nu mai folosim, transmitem direct prin UDP
import subprocess
import threading

from config import USB_DEVICE, USB_WIDTH, USB_HEIGHT, USB_FPS, USB_INPUT_FORMAT, USB_LOG_EVERY_N_FRAMES

_lock = threading.Lock()
_last_jpeg = None
_stop = False


def _camera_loop(dev, w, h, fps, input_format):
    global _last_jpeg, _stop

    # acceptă fie "/dev/video0", fie index int
    if isinstance(dev, int):
        dev_path = f"/dev/video{dev}"
    else:
        dev_path = str(dev)

    cmd = [
        "ffmpeg",
        "-hide_banner", "-loglevel", "error",
        "-f", "v4l2",
        "-input_format", input_format,
        "-video_size", f"{w}x{h}",
        "-framerate", str(fps),
        "-i", dev_path,
        "-c:v", "copy",
        "-f", "mjpeg",
        "pipe:1",
    ]

    print("[USB] ffmpeg passthrough:", " ".join(cmd), flush=True)

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
    except FileNotFoundError:
        print("[USB] ffmpeg nu este instalat", flush=True)
        return

    SOI = b"\xff\xd8"
    EOI = b"\xff\xd9"
    buf = b""
    frames = 0

    while not _stop:
        chunk = proc.stdout.read(65536)
        if not chunk:
            if proc.poll() is not None:
                err = proc.stderr.read().decode(errors="ignore")
                print(f"[USB] ffmpeg oprit, code={proc.returncode}", flush=True)
                if err:
                    print("[USB ERR]", err, flush=True)
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

            """frames += 1
            if USB_LOG_EVERY_N_FRAMES and frames % USB_LOG_EVERY_N_FRAMES == 0:
                print(f"[USB] cadre MJPEG: {frames}")"""

            with _lock:
                _last_jpeg = frame

    try:
        proc.terminate()
    except Exception:
        pass
    print("[USB] passthrough oprit", flush=True)


def start_usb_camera():
    t = threading.Thread(
        target=_camera_loop,
        args=(USB_DEVICE, USB_WIDTH, USB_HEIGHT, USB_FPS, USB_INPUT_FORMAT),
        daemon=True,
    )
    t.start()
    print("[USB] camera_loop pornit", flush=True)


def get_usb_jpeg():
    with _lock:
        return _last_jpeg
