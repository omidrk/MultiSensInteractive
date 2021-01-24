import eventlet
import socketio

from arduino import MIS_Arduino
from threading import Lock
from time import sleep
import json

# create the arduino object and lock
arduino = MIS_Arduino("/dev/ttyACM0", 11520)
lockduino = Lock()

# creates the socket.IO and relative server
sio = socketio.Server(async_mode='eventlet')                 
app = socketio.WSGIApp(sio)

def send_reading():
    ' helper function to keep sending data over the socket.io '
    while True:
        if arduino.sent == False:
            with lockduino:
                msg = arduino.state_dict()
            sio.emit("status", msg, to=sid)
            #print("SENT: ", msg)
        eventlet.sleep(0)

# connection event
@sio.event
def connect(sid, environ):
    print('CONNECTED: ', sid)
    return True

# disconnection event
@sio.event
def diconnect(sid):
    print('DISCONNECTED: ', sid)

# command event
@sio.event
def command(sid, data):
    with lockduino:
        arduino.command(data)
    print("COMMANDED: ", data)

# upon connection tigger the send_reading helper function
@sio.on('connect')
def sensor_start(sid, environ):
    sio.start_background_task(send_reading, sid)
    


if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
    print("STARTED")