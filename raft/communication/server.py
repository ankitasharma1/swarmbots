from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from time import sleep, time, strftime, gmtime
from threading import Thread, Lock
from sys import exit
from select import select

PADDING_BTYE = b' '
MSG_SIZE = 1024 # bytes
RECV_TIMEOUT = .5 

class Server():
    def __init__(self, host, port, swarmer_id, debug=False):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.host = host
        self.port = port
        self.swarmer_id = swarmer_id
        self.clients = {}
        self.lock = Lock()
        self.debug = debug
        
        while True:
            try:
                self.sock.bind(('', port))
                self.sock.listen(1)
                self.debug_print(f"Listening on {host}:{port} ...")
                break
            except Exception as e:
                self.debug_print("Error binding or listening, retrying in 5 seconds")
                self.debug_print(f"{e}")
                sleep(5)

        t = Thread(target=self.advertise)
        t.setDaemon(True)
        t.start()

    def advertise(self):
        while True:
            self.debug_print(f"Advertising on {self.host}:{self.port}")
            client_conn, client_addr = self.sock.accept()
            self.register_client(client_conn, client_addr)
            self.debug_print(f"Connected to {client_addr}")

    def register_client(self, client_conn, client_addr):
        self.lock.acquire()
        self.clients[client_addr[0]] = client_conn
        self.lock.release()
    
    def remove_client(self, client_addr):
        self.lock.acquire()
        self.clients.pop(client_addr, None)
        self.lock.release()

    def send(self, client_addr, msg):
        if not client_addr in self.clients:
            self.debug_print(f"Error sending message, {client_addr} not in clients dict")
            return False
        else:
            try:
                byte_msg = msg.encode('utf-8')
                padded_msg = byte_msg + bytearray(PADDING_BTYE * (MSG_SIZE - len(byte_msg)))
                self.clients[client_addr].send(padded_msg)
                self.debug_print("Message sent.")
                return True
            except Exception as e:
                self.debug_print("Error sending message")
                self.debug_print(f"{e}")
                self.remove_client(client_addr)
                return False

    def client_addresses(self):
        return list(self.clients.keys())

    def get_client_name_local(self, client_addr):
        self.send(client_addr, 'who are you?')
        return self.recv(client_addr)

    def recv(self, client_addr, msg_timeout=RECV_TIMEOUT, msg_size=MSG_SIZE):
        if not client_addr in self.clients:
            self.debug_print(f"Error receiving message, {client_addr} not in dict")
            return None
        else:
            try:
                ready = select([self.clients[client_addr]], [], [], msg_timeout)
                if ready[0]:
                    data = self.clients[client_addr].recv(msg_size)
                    return data.decode('utf-8').rstrip()
                else:
                    return None
            except Exception as e:
                self.debug_print("Error receiving message")
                self.debug_print(f"{e}")
                self.remove_client(client_addr)

    def debug_print(self, print_string):
        if self.debug:
            time_string = strftime("%H:%M:%S", gmtime())
            id_string = f" {self.swarmer_id} Server: "
            print(time_string + id_string + print_string)

    def clean_up(self):
        self.sock.close()

if __name__ == '__main__':
    host = 'localhost'
    port = 5000
    start = time()
    s = Server(host, port, 'S1', True)
    while time() - start < 60:
        print("In client loop ...")
        for c in s.client_addresses():
            if not c in s.clients:
                print(f"{c} not connected")
            else:
                print(f"Checking for messages from {c}")
                msg = s.recv(c)
                if msg:
                    print(f"Message from {c}: {msg}")
                else:
                    print(f"No message from {c}")
                s.send(c, f"some message from {c}")
                # print(s.get_client_name_local(c))
                sleep(1)
                print("Done checking messages")
        sleep(1)
    s.clean_up()
    print("goodbye.")
