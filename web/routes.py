# web/routes.py

import time
from flask import Response, render_template

from cameras import get_usb_jpeg
from processing.qr_worker import get_qr_jpeg

#doar returneaza bytes JPEG
def _mjpeg_generator(frame_supplier):
    while True:
        frame = frame_supplier()
        if frame is None:
            time.sleep(0.01)
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            frame +
            b"\r\n"
        )


def init_routes(app):

    @app.route("/")
    def index():
        return render_template("indexNoVideo.html")

    @app.route("/stream.mjpg")
    def stream_mjpg():
        return Response(
            _mjpeg_generator(get_usb_jpeg),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    @app.route("/stream_phone_qr.mjpg")
    def stream_phone_qr():
        return Response(
            _mjpeg_generator(get_qr_jpeg),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
