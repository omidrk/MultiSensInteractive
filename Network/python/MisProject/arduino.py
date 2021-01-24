from functools import partial
from time import time
from MisProject.utils import area, ECG_Queue

class MIS_Arduino:
    def __init__(self, serial, baud):
        self.HIGH_PRESSURE_THRESHOLD = 800
        self.LOW_PRESSURE_THRESHOLD = 300
        self.R_THRESHOLD = 620

        self.serial = serial
        self.baud = baud

        # sensor device time of last read
        self.last_read = 0

        # ECG Readings
        self.ECG = 0
        self.lop = 0
        self.lom = 0
        self.delta = 0

        # BPM parameters
        self.last_beat = 0
        self.BPM = 0
        self.in_beat = False
        self.ECG_Queue = ECG_Queue(500)

        # contains last read
        self.pressure = {}

        # contains the number of steps
        self.steps = {}

        # contains the pressed status
        self.is_pressed = {}

        # cointains the reads from IMU
        self.x = 0
        self.y = 0
        self.z = 0

        # contains texture from the VR Headeset
        self.texture = None
        
        # contains relay status
        self.relays = {}

        # contains if the data was sent by serial
        self.sent = False

        # partial function to control the relay
        self.windspan = partial(area, 5)
        self.shift = 1

    def read_update(self, read):
        ' From the read provided in a dictionary format updates the fields '
        try:
            self.last_read = read["time"]
            self.ECG = read["ECG"]
            self.lop = read["lop"]
            self.lom = read["lom"]
            self.pressure[1] = read["pressure1"]
            self.pressure[2] = read["pressure2"]
            self.x = read["x"]
            self.y = read["y"]
            self.z = read["z"]
            self.sent = False
        except Exception as e:
            print("ARDUINO INVALID READ: ", read, "\n\t", e)
            return False

        # calls the handle function for the pressure sensors
        try:
            self.pressure_handle(1)
            self.pressure_handle(2)
        except Exception as e:
            print("ARDUINO ERROR PRESSURE HANDLE: " "\n\t", e)

        # calls the handle function for the ECG read
        try:
            self.ECG_handle()
        except Exception as e:
            print("ARDUINO ERROR ECG HANDLE: " "\n\t", e)

    def pressure_handle(self, key_id):
        ' Makes the pressure sensor act like a button '
        pressure = self.pressure.setdefault(key_id, None)
        is_pressed = self.is_pressed.setdefault(key_id, False)
        self.steps.setdefault(key_id, 0)
        if pressure == None:
            return False
        
        # changes status of the is_pressed dictionary based on the threshold
        elif (pressure > self.HIGH_PRESSURE_THRESHOLD) and not is_pressed:
            self.is_pressed[key_id] = True
        elif (pressure < self.LOW_PRESSURE_THRESHOLD) and is_pressed:
            self.is_pressed[key_id] = False
            self.steps[key_id] += 1

    def ECG_handle(self):
        '''
            Handls the ECG update
        '''
        if self.lop or self.lom:
            print("ARDUINO ECG LOP LOM INVALID READ")
            return None
        
        if self.ECG < self.R_THRESHOLD:
            if self.in_beat:
                self.in_beat = False
            return None
    
        if self.in_beat: return None

        self.in_beat = True
        dt = time() - self.last_beat
        self.ECG_Queue.push(60000/dt)
        self.BPM = self.ECG_Queue.bpm()

        self.last_beat = self.last_read


    def texture_command(self, json_dict):
        '''
            Main method handling for commands sent by the VR headset
        '''
        # texture update command
        if json_dict.get("id", False) and json_dict.get("value", False):
            try:
                text_id, status = json_dict["id"], json_dict["value"]
                if status == 1:
                    self.texture = text_id
            except Exception as e:
                print(e)
                print("ARDUINO INVALID TEXTURE COMMAND: ", json_dict)
                return False

    def fan_command(self, json_dict):
        # fan setting command
        if json_dict.get("fan", False) and json_dict.get("state", False):
            try:
                pin, state = json_dict["fan"], json_dict["state"]
                self.relays[pin] = state
            except Exception as e:
                print(e)
                print("ARDUINO INVALID FAN COMMAND: ", json_dict)
                return False

    def wind_command(self, json_dict):   
        # wind setting command
        if json_dict.get("yaw", False):
            try:
                direction = json_dict["yaw"]

                # normalises direction to [0, 1]
                if direction < 0:
                    direction = direction + 360
                direction = direction/360

                # updates the relays to recreate
                self.relays = {i+self.shift : self.windspan(i, direction) for i in range(1, 5)}
            except Exception as e:
                print(e)
                print("ARDUINO INVALID WIND COMMAND: ", json_dict)
                return False
        
    def state_dict(self):
        " Rendes the dictionary of the object for communication "
        return { "X": self.x, "Y": self.y, "Z": self.z, "BPM": self.BPM }


if __name__ == "__main__":
    arduino = MIS_Arduino("/dev/ttyACM0", 11520)

    print(arduino.state_dict())

