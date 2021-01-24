import select, socket, queue, json
from arduino import MIS_Arduino
from threading import Thread, Lock
from time import time

def socket_data_process(from_socket):
    from_socket.strip()
    #print(from_socket)
    head, message = from_socket[:5], from_socket[6:]
    #print(head, message)
    head = int(head)
    #print(head)
    return json.loads(message[:head])



def socket_loop(arduino, lockduino):
    t0 = time()
    i = 0

    HEADER_LEN = 5
    SENSOR_LEN = 506
    COMMAND_LEN = 250

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setblocking(False)
    client.bind((client.getsockname()[0], 50001))
    client.listen(5)
    inputs = [client]
    outputs = []
    message_queues = {}

    while inputs:
        # get all the connections
        readable, writable, exceptional = select.select(inputs, outputs, inputs)

        # process readable sockets
        for s in readable:
            #  if the readable socket is this client
            # means that a new connection has arrived
            if s is client:
                # accept the connection
                connection, client_address = s.accept()
                print(f"SOCKET ACCEPTED: {client_address}")
                connection.setblocking(False)
                # set the connection in the inputs
                inputs.append(connection)
                # generate a connection queue fot the new connection
                message_queues[connection] = queue.Queue()

            # if the socket is not this client
            else:
                # read 1024 bytes of data
                data = s.recv(COMMAND_LEN + HEADER_LEN + 1)
                if data:
                    # commands a variation in the arduino
                    #print(f"SOCKET GOT: {data}")
                    try:
                        data = socket_data_process(data)
                        #print(data)
                    except ValueError as v:
                        print("SOCKET SEND/REC ERROR: ", data)
                        continue

                    with lockduino:
                        arduino.command(data)
                    # push the data connection queue
                    ## message_queues[s].put(data)
                    if s not in outputs:
                        outputs.append(s)
                    
                else:
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                    del message_queues[s]

        for s in writable:
            with lockduino:
                MESSAGE = arduino.state_dict()
            i += 1
            try:
                MESSAGE = json.dumps(MESSAGE)
                #print("SOCKET SENT", i/(time()-t0))
                MESSAGE =  f"{len(MESSAGE):>{HEADER_LEN}}:" + f"{MESSAGE:<{SENSOR_LEN}}"
                s.send(bytes(MESSAGE, 'utf8'))
            except Exception as e:
                print("SENDING ERROR: ", MESSAGE)
        
        for s in exceptional:
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()
            del message_queues[s]
                    
if __name__ == "__main__":
    arduino = MIS_Arduino("/dev/ttyACM0", 11520)
    lockduino = Lock()

    t_socket = Thread(target=socket_loop, args=(arduino,))

    t_socket.start()


    t_socket.join()
