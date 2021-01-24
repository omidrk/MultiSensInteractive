from MisProject.serial_reader import serial_loop
from MisProject.OSCserver import osc_loop
from MisProject.arduino import MIS_Arduino
from threading import Thread, Lock

import eventlet
import socketio
import json

# create the arduino object and lock
arduino = MIS_Arduino("/dev/ttyACM0", 115200)
lockduino = Lock()

static_files = {
    '/': './public/index.html',
    '/jquery.js': './public/jquery.js',
    '/socket.io.js': './public/socket.io.js',
}

# creates the socket.IO and relative server
# sio = socketio.Server(async_mode='eventlet')                 
# app = socketio.WSGIApp(sio, static_files=static_files)
sio = socketio.Client(logger=True, engineio_logger=True)

async def send_reading(sio):
    
    ' helper function to keep sending data over the socket.io '
    while True:
        print('in the loppppppppp')
        if arduino.sent == False:
            with lockduino:
                msg = arduino.state_dict()
                arduino.sent = True
                await sio.emit("sensorWalk", json.dumps(msg))
            #print("SENT: ", msg)
        # eventlet.sleep(0)
#sending_loop = Thread(target=send_reading, args=(sio))

# connection event
@sio.event
def connect():
    print('CONNECTED: ')
    # sio.emit("sensorWalk", "{'foo':'bar'}")
    sio.start_background_task(send_reading,sio)
    #sending_loop.start()
    # def sensor_start(sio):
        # sio.start_background_task(send_reading)
        # sio.start_background_task()

# disconnection event
@sio.event
def diconnect():
    print('DISCONNECTED: ')

# fan command event
@sio.event
def fan(data):
    with lockduino:
        arduino.fan_command(data)
    print("COMMANDED: ", data)

# wind command event
@sio.event
def wind(data):
    with lockduino:
        arduino.wind_command(data)
    print("WIND COMMANDED: ", data)

# texture command event
@sio.event
def walkingMat(data):
    with lockduino:
        arduino.texture_command(data)
    print("WIND COMMANDED: ", data)

  

t_serial = Thread(target=serial_loop, args=(arduino, lockduino))
t_osc = Thread(target=osc_loop, args=(arduino, lockduino))

# start serial read thread
t_serial.start()
print("SERIAL STARTED")

# start the OSC thread
t_osc.start()
print("OPEN SOUND CONTROL STARTED")

# start the socket.io server
print("Client STARTED")
# eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app, log_output=False)

#sio.wait()
sio.connect('http://192.168.0.102:5000')
sio.wait()
#async def connect_me(sio):
#    await 
    
    

t_serial.join()
t_osc.join()







