import bluetooth as BT
from time import sleep, gmtime, strftime
from select import select

if __name__ != '__main__':
    from .MSG_CONFIG import PADDING_BYTE, MSG_SIZE, RECV_TIMEOUT
else:
    from MSG_CONFIG import PADDING_BYTE, MSG_SIZE, RECV_TIMEOUT


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


class BT_Client:
    def __init__(self, swarmer_id, debug=False):
        self.bt_sock = BT.BluetoothSocket(BT.RFCOMM) 
        self.swarmer_id = swarmer_id
        self.debug = debug
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
            except BT.btcommon.BluetoothError:
                self.debug_print(f"Connection to server {host}--{port} unsuccessful, retrying in 3 seconds")
                self.bt_sock = BT.BluetoothSocket(BT.RFCOMM) 
                sleep(3)
        self.connected = True
        self.debug_print(f"Connected to {host} on port {port}")
        return True

    @failsafe
    def send(self, msg):
        byte_msg = msg.encode('utf-8')
        padded_msg = byte_msg + bytearray(PADDING_BYTE * (MSG_SIZE - len(byte_msg)))
        self.bt_sock.sendall(padded_msg)
        self.debug_print(f"Message sent to {self.host}--{self.port}")
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
    from BT_CONFIG import BT_DICT
    from SWARMER_ID import SWARMER_ID  # only exists locally
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 bt_client [s_id to connect to]")
        sys.exit(1)

    s_id = sys.argv[1]

    if s_id not in BT_DICT:
        print(f"Error: {s_id} not valid swarmer id: {list(BT_DICT.keys())}")
        sys.exit(1)

    c = BT_Client(SWARMER_ID, True)
    to_host = BT_DICT[s_id]["ADDR"]
    to_port = BT_DICT[s_id][f"{SWARMER_ID}_PORT"]
    c.connect(to_host, to_port)

    msg = f"Hello from {SWARMER_ID}!!!"
    while True:
        try:
            c.send(msg)
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Stopping clients safely ...")
            break

    c.clean_up()

    print("Clients stopped safely. Goodbye.")
