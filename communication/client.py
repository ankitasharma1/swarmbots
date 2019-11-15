from socket import socket, AF_INET, SOCK_STREAM
from time import sleep, gmtime, strftime

def failsafe(func):
    def wrapper(*args, **kw_args):
        try:
            return func(*args, **kw_args)
        except Exception as e:
            self = args[0]
            self.debug_print(f"{e}")
            try:
                self.sock.close()
                self.sock = socket(AF_INET, SOCK_STREAM)
                self.sock.settimeout(self.timeout)
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

class Client():
    def __init__(self, swarmer_id, debug=False, timeout=5):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.connected = False
        self.host = None
        self.port = None
        self.swarmer_id = swarmer_id
        self.timeout = timeout
        self.debug = debug

        self.sock.settimeout(timeout)

    @failsafe
    def connect(self, host, port):
        self.debug_print(f"Connecting to {host} on port {port} ...")
        self.host = host
        self.port = port
        while True:
            try:
                self.sock.connect((host, port))
                break
            except ConnectionRefusedError:
                self.debug_print(f"Connection refused by server {host}:{port}, retrying in 5 seconds")
                sleep(5)
        self.connected = True
        self.debug_print(f"Connected to {host} on port {port}")
        return True

    @failsafe
    def send(self, msg):
        self.sock.sendall(msg.encode('utf-8'))
        self.debug_print("Message sent.")
        return True

    @failsafe
    def recv(self, msg_size=1024):
        while True:
            data = self.sock.recv(msg_size)
            if data:
                return data.decode('utf-8')

    def debug_print(self, print_string):
        if self.debug:
            time_string = strftime("%H:%M:%S", gmtime())
            id_string = f" {self.swarmer_id} Client: "
            print(time_string + id_string + print_string)

    def clean_up(self):
        self.sock.close()

if __name__ == '__main__':
    host = 'localhost'
    port = 5000
    c = Client('YO', True)
    c.connect(host, port)
    sleep(1)
    c.send("hello")
    sleep(1)
    print(c.recv())
    sleep(1)
    c.clean_up()
    print("goodbye.")
