from flask import Flask
from flask_socketio import SocketIO
import threading
from web.routes import init_routes
from web.sockets import init_sockets

from config import CORS_ALLOWED_ORIGINS, HOST, PORT
from cameras.usb import start_usb_camera
from cameras.ip import start_ip_capture
from processing.qr_worker import start_qr_worker
from control.motors import init_motors
from I2C.PCA import init_servos, update_grip
from I2C.bmp import init_bmp280
from I2C.ampermeter import init_amp


app = Flask(__name__, template_folder="templates", static_folder="static")
socketio = SocketIO(app, cors_allowed_origins=CORS_ALLOWED_ORIGINS , async_mode="threading")

def bootstrap():
    init_amp()
    init_motors()
    init_servos()
    init_bmp280()
    #start_usb_camera()
    start_ip_capture() #THREAD
    start_qr_worker(socketio) #THREAD

    init_routes(app)
    init_sockets(socketio)

if __name__ == "__main__":
    bootstrap()
    thread_grip = threading.Thread(target = update_grip)
    thread_grip.start()
    socketio.run(app, host=HOST, port=PORT)

