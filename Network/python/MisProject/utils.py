
def area(N, i, x):
    """
        N is the number of the relays
        i is the numbero of the relay of which is asked
        x is the read categoried

        This function categorises the read form x [0, 1]
        The space is divided into 2*N areas in which:
            N activate a single relay
            N activate 2 relays
        Simulates wind on on/of relays
    """
    m = ( 2 * (i-1)) / (2*N)
    M = (2*i + 1) / (2*N)

    if M >= 1 and (x >= m or  x <= (M-1)):
        return 1
    elif m <= x <= M:
        return 1
    else:
        return 0


class ECG_Queue:
    def __init__(self, capacity):
        self.capacity = capacity
        self.storage = []
        self.sum = 0

    def push(self, value):
        self.storage.append(value)
        self.sum += value
        if len(self.storage) > self.capacity:
            self.sum -= self.storage.pop(0)

    def bpm(self):
        return self.sum / self.capacity            

