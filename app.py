from flask import Flask
from flask_socketio import SocketIO
from config import CORS_ALLOWED_ORIGINS, HOST, PORT
from web.routes import init_routes
from web.sockets import init_sockets
from cameras.usb import start_usb_camera
from cameras.ip import start_ip_capture
from processing.qr_worker import start_qr_worker
from control.motors import init_motors
from I2C.PCA import init_servos
from I2C.bmp import init_bmp280

app = Flask(__name__, template_folder="templates", static_folder="static")
socketio = SocketIO(app, cors_allowed_origins=CORS_ALLOWED_ORIGINS , async_mode="threading")

def bootstrap():
    init_motors()
    init_servos()
    init_bmp280()
    #start_usb_camera()
    start_ip_capture()
    start_qr_worker(socketio)

    init_routes(app)
    init_sockets(socketio)

if __name__ == "__main__":
    bootstrap()
    socketio.run(app, host=HOST, port=PORT)
