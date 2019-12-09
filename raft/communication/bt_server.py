import bluetooth as BT
from time import sleep, time, strftime, gmtime
from threading import Thread, Lock
from select import select

if __name__ != '__main__':
    from .MSG_CONFIG import PADDING_BYTE, MSG_SIZE, RECV_TIMEOUT, MSG_SEND_DELAY, MSG_RECV_DELAY
else:
    from MSG_CONFIG import PADDING_BYTE, MSG_SIZE, RECV_TIMEOUT, MSG_SEND_DELAY, MSG_RECV_DELAY


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
                self.debug_print(f"Listening on {host}--{port} ...")
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
            self.debug_print(f"Advertising on {self.host}--{self.port}")
            # print(f"Advertising on {self.host}--{self.port}") # TODO: delete
            client_conn, client_info = self.bt_sock.accept()
            self.register_client(client_conn, client_info[0])
            self.debug_print(f"Connected to {client_info[0]}")
            # print(f"Connected to {client_info[0]}") # TODO: delete
            print(f">>> Connected to {client_info[0]}--{client_info[1]}")

    def register_client(self, client_conn, client_addr):
        self.lock.acquire()
        self.clients[client_addr] = client_conn
        self.lock.release()
    
    def remove_client(self, client_addr):
        self.lock.acquire()
        self.clients.pop(client_addr, None)
        self.lock.release()
    
    # TODO: update calls after merge!!!
    def send(self, msg, client_addr="any", msg_delay=MSG_SEND_DELAY):
        if client_addr == "any":
            for addr, client in self.clients.items():
                try:
                    byte_msg = msg.encode('utf-8')
                    padded_msg = byte_msg + bytearray(PADDING_BYTE * (MSG_SIZE - len(byte_msg)))
                    client.sendall(padded_msg)
                    self.debug_print(f"Message sent to {addr}")
                    sleep(msg_delay)
                    return True
                except Exception as e:
                    self.debug_print("Error sending message")
                    self.debug_print(f"{e}")
                    self.remove_client(addr)
                    sleep(msg_delay)
                    return False
                
        if client_addr not in self.clients:
            self.debug_print(f"Error sending message, {client_addr} not in clients dict")
            sleep(msg_delay)
            return False
        else:
            try:
                byte_msg = msg.encode('utf-8')
                padded_msg = byte_msg + bytearray(PADDING_BYTE * (MSG_SIZE - len(byte_msg)))
                self.clients[client_addr].sendall(padded_msg)
                self.debug_print(f"Message sent to {client_addr}")
                sleep(msg_delay)
                return True
            except Exception as e:
                self.debug_print("Error sending message")
                self.debug_print(f"{e}")
                self.remove_client(client_addr)
                sleep(msg_delay)
                return False
    
    def client_addresses(self):
        return list(self.clients.keys())
    
    def recv(self, client_addr, msg_timeout=RECV_TIMEOUT, msg_delay=MSG_RECV_DELAY, msg_size=MSG_SIZE):
        if client_addr not in self.clients:
            self.debug_print(f"Error receiving message, {client_addr} not in clients dict")
            sleep(msg_delay)
            return None
        else:
            try:
                ready = select([self.clients[client_addr]], [], [], msg_timeout)
                if ready[0]:
                    data = self.clients[client_addr].recv(msg_size)
                    sleep(msg_delay)
                    msg = data.decode('utf-8').rstrip()
                    self.debug_print(f"Received \"{msg}\" from {client_addr}")
                    return msg
                else:
                    sleep(msg_delay)
                    return None
            except Exception as e:
                self.debug_print("Error receiving message")
                self.debug_print(f"{e}")
                self.remove_client(client_addr)
                sleep(msg_delay)
                return None
    
    def debug_print(self, print_string, override=False):
        if self.debug or override:
            time_string = strftime("%H:%M:%S", gmtime())
            id_string = f" {self.swarmer_id} Server: "
            print(time_string + id_string + print_string)

    def clean_up(self):
        self.bt_sock.close()


if __name__ == "__main__":
    # testing
    from BT_CONFIG import BT_DICT, BT_ADDR_DICT, S_IDS
    from SWARMER_ID import SWARMER_ID

    servers = []
    recv_counts = {}
    for s_id in S_IDS:
        if s_id == SWARMER_ID:
            print(f"Detected my s_id: {s_id}, not creating a server")
            continue
        else:
            recv_counts[s_id] = 0
            s = BT_Server(BT_DICT[SWARMER_ID]["ADDR"], BT_DICT[SWARMER_ID][f"{s_id}_PORT"], SWARMER_ID)
            servers.append(s)

    while True:
        try:
            for server in servers:
                for client_addr in list(server.clients.keys()):
                    # print(f"Checking for messages from {BT_ADDR_DICT[client_addr]}")
                    msg = server.recv(client_addr)
                    if msg:
                        recv_counts[BT_ADDR_DICT[client_addr]] += 1
                        if recv_counts[BT_ADDR_DICT[client_addr]] % 100 == 0:
                            server.debug_print(f"{recv_counts[BT_ADDR_DICT[client_addr]]} messages received from {BT_ADDR_DICT[client_addr]}", True)
                    else:
                        print(f"No messages from {BT_ADDR_DICT[client_addr]}")
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Stopping servers safely ...")
            break

    for s in servers:
        s.clean_up()

    print("Servers stopped safely. Goodbye.")
