import bluetooth as BT
from time import sleep, time, strftime, gmtime
from threading import Thread, Lock
from select import select

from .MSG_CONFIG import PADDING_BYTE, MSG_SIZE, RECV_TIMEOUT


class BT_Server:
    def __init__(self, host, port, swarmer_id, debug=False):
        self.bt_sock = BT.BluetoothSocket(BT.RFCOMM)
        self.host = host
        self.port = port
        self.swarmer_id = swarmer_id
        self.debug = debug
        
        self.clients = {}
        self.lock = Lock()

        self.name = swarmer_id + " Server"
        
        while True:
            try:
                self.bt_sock.bind((host, port))
                self.bt_sock.listen(1)
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
            client_conn, client_info = self.bt_sock.accept()
            self.register_client(client_conn, client_info[0])
            self.debug_print(f"Connected to {client_info[0]}")
            # print(f"Connected to {self.client_info[0]} on port {self.client_info[1]}")

    def register_client(self, client_conn, client_addr):
        self.lock.acquire()
        self.clients[client_addr] = client_conn
        self.lock.release()
    
    def remove_client(self, client_addr):
        self.lock.acquire()
        self.clients.pop(client_addr, None)
        self.lock.release()
    
    # TODO: update calls after merge!!!
    def send(self, msg, client_addr="any"):
        if client_addr == "any":
            for addr, client in self.clients.items():
                try:
                    byte_msg = msg.encode('utf-8')
                    padded_msg = byte_msg + bytearray(PADDING_BYTE * (MSG_SIZE - len(byte_msg)))
                    client.sendall(padded_msg)
                    self.debug_print("Message sent.")
                    return True
                except Exception as e:
                    self.debug_print("Error sending message")
                    self.debug_print(f"{e}")
                    self.remove_client(addr)
                    return False
                
        if client_addr not in self.clients:
            self.debug_print(f"Error sending message, {client_addr} not in clients dict")
            return False
        else:
            try:
                byte_msg = msg.encode('utf-8')
                padded_msg = byte_msg + bytearray(PADDING_BYTE * (MSG_SIZE - len(byte_msg)))
                self.clients[client_addr].sendall(padded_msg)
                self.debug_print("Message sent.")
                return True
            except Exception as e:
                self.debug_print("Error sending message")
                self.debug_print(f"{e}")
                self.remove_client(client_addr)
                return False
    
    def client_addresses(self):
        return list(self.clients.keys())
    
    def recv(self, client_addr, msg_timeout=RECV_TIMEOUT, msg_size=MSG_SIZE):
        if client_addr not in self.clients:
            self.debug_print(f"Error receiving message, {client_addr} not in clients dict")
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
        self.bt_sock.close()


if __name__ == "__main__":
    # testing
    from .BT_CONFIG import BT_DICT
    from .SWARMER_ID import SWARMER_ID

    host = BT_DICT[SWARMER_ID]["ADDR"]
    port = BT_DICT[SWARMER_ID]["PORT"]

    s = BT_Server(host, port, SWARMER_ID, True)
    start = time()
    while time() - start < 60:
        print("Starting to check for messages ...")
        for c in s.client_addresses():
            if c not in s.clients:
                print(f"{c} not connected")
            else:
                print(f"Checking for messages from {c}")
                msg = s.recv(c)
                if msg:
                    print(f"Message from {c}: {msg}")
                else:
                    print(f"No message from {c}")
                s.send(c, f"some message from {SWARMER_ID}")
                sleep(1)
        print("Done checking messages")
        sleep(1)
    s.clean_up()
    print("goodbye.")

