import bluetooth as BT
from time import sleep, gmtime, strftime, time
from select import select

# TODO: put MSG_SIZE in global config file
PADDING_BTYE = b' '
MSG_SIZE = 1024 # bytes
RECV_TIMEOUT = 0.5

def failsafe(func):
    def wrapper(*args, **kw_args):
        try:
            return func(*args, **kw_args)
        except Exception as e:
            self = args[0]
            self.debug_print(f"{e}")
            try:
                self.bt_sock.close()
                self.bt_sock = BT.BluetoothSocket(BT.RFCOMM)
                self.bt_sock.settimeout(self.timeout)
                self.connected = False
                if self.connect(self.host, self.port):
                    self.debug_print("Reconnect successful, redoing last action")
                    return func(*args, **kw_args)
            except Exception as e:
                if type(e) == OSError or type(e) == IOError:
                    # OSError is raised when self.connect is what failed in the first place
                    # probably due to a timeout
                    pass
                else:
                    print(e)
                    print(f"{self.swarmer_id} Client: Unknown exception during failsafe process, exiting")
                    self.clean_up()
                return
    return wrapper

class BT_Client():
    def __init__(self, swarmer_id, timeout=5, debug=False):
        self.bt_sock = BT.BluetoothSocket(BT.RFCOMM) 
        self.swarmer_id = swarmer_id
        self.debug = debug
        self.bt_sock.settimeout(timeout)
        self.connected = False

        self.host = None
        self.port = None

    def connect(self, host, port):
        self.debug_print(f"Connecting to {host} on port {port} ...")
        self.host = host
        self.port = port
        while True:
            try:
                self.bt_sock.connect((host, port))
                break
            except ConnectionRefusedError:
                self.debug_print(f"Connection refused by server {host}:{port}, retrying in 5 seconds")
                sleep(5)
        self.connected = True
        self.debug_print(f"Connected to {host} on port {port}")
        return True

    @failsafe
    def send(self, msg):
        byte_msg = msg.encode('utf-8')
        padded_msg = byte_msg + bytearray(PADDING_BTYE * (MSG_SIZE - len(byte_msg)))
        self.bt_sock.send(padded_msg)
        self.debug_print("Message sent.")
        return True
    
    @failsafe
    def recv(self, msg_timeout=RECV_TIMEOUT, msg_size=MSG_SIZE):
        ready = select([self.bt_sock], [], [], msg_timeout)
        if ready[0]:
            data = self.bt_sock.recv(msg_size)
            return data.decode('utf-8').rstrip()
        else:
            return None
    
    def debug_print(self, print_string):
        if self.debug:
            time_string = strftime("%H:%M:%S", gmtime())
            id_string = f" {self.swarmer_id} Client: "
            print(time_string + id_string + print_string)

    def clean_up(self):
        self.bt_sock.close()
        self.connected = False

if __name__ == "__main__":
    # testing
    from SWARMER_BT_INFO import UUID, SWARMER_ID_DICT, SWARMER_ADDR_DICT
    from SWARMER_ID import SWARMER_ID

    # change below if testing client for swarmer2
    # host = SWARMER_ID_DICT["S2"]["ADDR"]
    # port = SWARMER_ID_DICT["S2"]["PORT"]
    host = SWARMER_ID_DICT["S3"]["ADDR"]
    port = SWARMER_ID_DICT["S3"]["PORT"]

    c = BT_Client(SWARMER_ID, debug=True)
    c.connect(host, port)
    start = time()
    while time() - start < 20:
        print('inside client loop')
        sleep(4)
        c.send(f"hello from {SWAMER_ID} the time is {gmtime()}")
        print("checking for messages")
        msg = c.recv()
        if msg:
            print(msg)
        else:
            print("no messages")
        sleep(1)
    c.clean_up()
    print('goodbye.')