import serial, json
from MisProject.arduino import MIS_Arduino
from time import time,sleep
from random import randint
from threading import Thread, Lock

SERIAL_PATH = "COM5"
BAUD = 115200

arduino = MIS_Arduino("/dev/ttyACM0", 115200)
lockduino = Lock()

def random_message():
    value = randint(2, 6)
    state = randint(0,1)
    return {"fan" : [value, state]}

def serial_loop(arduino, lockduino):
    connection = serial.Serial(arduino.serial,
                                arduino.baud)
                            
    i = 0
    t0 = time()

    #print(json.loads(message)["fan"])

    while True:
        i +=1
        # read incoming data  from serial
        incoming = connection.readline()

        # Almos allways the first json is incomplete
        try:
            incoming = json.loads(incoming)
            #sio.emit("sensorWalk", incoming)
        except Exception as e:
            #print(e)
            #print("SERIAL INPUT INVALID JSON: ", incoming)
            continue
        
        # acquire lock on the Arduino Object
        with lockduino:
            # update the Arduino Object with serial data
            arduino.read_update(incoming)
            # fetch the state of the Arduino Object
            state = arduino.__dict__
        
        # send the relay status as messages to the arduino via serial
        print(state)
        for k, v in state["relays"].items():
            message = {"fan" : [k, v]}
            message = json.dumps(message)
            connection.write(bytes(message, "utf-8"))



if __name__ == "__main__":
    arduino = MIS_Arduino("/dev/ttyACM0", 11520)
    lockduino = Lock()

    t_serial = Thread(target=serial_loop, args=(arduino, lockduino))

    t_serial.start()

    while True:
        with lockduino:
            value = randint(2, 6)
            state = randint(0,1)
            arduino.relays[value] = state
        sleep(0.2)

    t_serial.join()
