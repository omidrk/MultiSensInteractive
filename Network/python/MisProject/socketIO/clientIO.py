import socketio

from time import sleep
from random import randint
import json

sio = socketio.AsyncClient()

def random_message():
    value = randint(2, 5)
    state = randint(0, 1)
    return json.dumps({"fan" : [value, state]})

def command_loop():
    sio.emit('command', random_message())
    sleep(0.1)

@sio.event
def connect():
    print('CONNECTED')
    
@sio.event
def connect_error():
    print("CONNECT ERROR")

@sio.event
def status(data):
    pass
    #print('GOT: ', data)
    
@sio.event
def disconnect():
    print('DISCONNECTED')

@sio.on("connect")
def mock_command():
    sio.start_background_task(command_loop)

await sio.connect('http://localhost:5000')

await sio.wait()