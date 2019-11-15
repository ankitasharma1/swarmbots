from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from time import sleep, time, strftime, gmtime
from threading import Thread, Lock
from sys import exit


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
                self.sock.bind((host, port))
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
        self.clients[client_addr] = client_conn
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
                self.clients[client_addr].sendall(msg.encode('utf-8'))
                self.debug_print("Message sent.")
                return True
            except Exception as e:
                self.debug_print("Error sending message")
                self.debug_print(f"{e}")
                self.remove_client(client_addr)
                return False

    def client_addresses(self):
        return list(self.clients.keys())

    def recv(self, client_addr, msg_size=1024):
        if not client_addr in self.clients:
            self.debug_print(f"Error receiving message, {client_addr} not in clients dict")
            return None
        else:
            try:
                data = self.clients[client_addr].recv(msg_size)
                if data:
                    return data.decode('utf-8')
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
        print("Waiting for messages ...")
        for c in s.client_addresses():
            if not c in s.clients:
                print(f"{c} not connected")
            else:
                print(f"Checking for messages from {c}")
                msg = s.recv(c)
                if msg:
                    print(f"Message from {c}: {msg}")
                s.send(c, f"some message from {c}")
        sleep(1)
    s.clean_up()
    print("goodbye.")
