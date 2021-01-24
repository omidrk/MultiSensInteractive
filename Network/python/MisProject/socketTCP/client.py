import socket, queue, select, sys
from time import time, sleep
from random import randint
import json

"""
999:MESSAGE
"""



to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
to_server.connect(('192.168.1.81', 50001))

inputs = [to_server]
outputs = [to_server]
command_queue = queue.Queue()

HEADER_LEN = 5
SENSOR_LEN = 506
COMMAND_LEN = 250

i = 0

def random_message():
    value = randint(2, 5)
    state = randint(0,1)
    return json.dumps({"fan" : [value, state]})

while True:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    for s in readable:
        if s == to_server:
            data = s. recv(SENSOR_LEN + HEADER_LEN + 1)
            if not data: break
            #print(data)
    
    for s in writable:
        if s == to_server:
            i += 1

            if i % 10 == 0: 
                MESSAGE = random_message()
                msg =  f"{len(MESSAGE):>{HEADER_LEN}}:" + f"{MESSAGE:<{COMMAND_LEN}}"
                s.send(bytes(msg, 'utf8'))

    
    for s in exceptional:
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        print(f"REMOVED: {s}")
        s.close()

